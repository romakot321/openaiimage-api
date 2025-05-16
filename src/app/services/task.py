from io import BytesIO
import json
from aiohttp import ClientSession
import asyncio
from typing import Any, Coroutine
from PIL import Image
from loguru import logger
from uuid import UUID
from fastapi import Depends, HTTPException
import base64
import os

from pydantic import BaseModel

from app.db.tables import ContextEntityRole, TaskItem
from app.repositories.openai import OpenAIRepository
from app.repositories.prompt import PromptRepository
from app.repositories.task import TaskRepository
from app.repositories.task_request import TaskRequestRepository
from app.schemas.external import (
    ExternalImage2ImageTaskSchema,
    ExternalResponse,
    ExternalText2ImageTaskSchema,
    ExternalText2TextTaskSchema,
)
from app.repositories.storage import StorageRepository
from app.schemas.task import (
    TaskImageCreateSchema,
    TaskSchema,
    TaskShortSchema,
    TaskStatisticsSchema,
    TaskTextCreateSchema,
)
from app.services.context import ContextService


remaining_requests: int | None = None
remaining_tokens: int | None = None
remaining_reset_in: str | None = None


class TaskService:
    external_url = os.getenv("EXTERNAL_URL")
    sended_tasks: list[UUID] = []

    def __init__(
        self,
        task_repository: TaskRepository = Depends(TaskRepository.depend),
        prompt_repository: PromptRepository = Depends(PromptRepository.depend),
        request_repository: TaskRequestRepository = Depends(
            TaskRequestRepository.depend
        ),
        openai_repository: OpenAIRepository = Depends(),
        storage_repository: StorageRepository = Depends(),
    ):
        global remaining_requests, remaining_tokens, remaining_reset_in
        self.remaining_requests = remaining_requests
        self.remaining_tokens = remaining_tokens
        self.remaining_reset_in = remaining_reset_in

        self.task_repository = task_repository
        self.external_repository = openai_repository
        self.prompt_repository = prompt_repository
        self.request_repository = request_repository
        self.storage_repository = storage_repository

    async def create(self, schema: TaskImageCreateSchema | TaskTextCreateSchema) -> TaskShortSchema:
        if isinstance(schema, TaskImageCreateSchema) and schema.user_prompt is None and schema.model_id is None:
            raise HTTPException(
                422, detail="Model id and prompt cannot be None at one time"
            )

        if schema.context_id == "last":
            async with ContextService() as context_service:
                schema.context_id = (await context_service.get_last(schema.user_id)).id

        model = await self.task_repository.create(
            user_id=schema.user_id,
            app_bundle=schema.app_bundle,
            context_id=schema.context_id,
        )
        return TaskShortSchema.model_validate(model)

    def _convert_image(self, image_buffer: BytesIO) -> BytesIO:
        converted = BytesIO()
        image = Image.open(image_buffer)
        image = image.convert("RGB")
        # [image.putpixel((x, y), image.getpixel((x, y))[:3] + (0,)) for x in range(image.size[0]) for y in range(image.size[1])]
        # logger.debug(image.getpixel((0, 0)))
        image.save(converted, format="PNG", mode="RGB")
        converted.seek(0)
        return converted

    async def build_prompt(
        self, schema: TaskImageCreateSchema | TaskTextCreateSchema, include_context: bool = True
    ) -> str:
        if isinstance(schema, TaskTextCreateSchema):
            return schema.prompt

        prompt = ""

        if schema.context is not None and include_context:
            for entity in schema.context.entities:
                if entity.content in schema.context.images_filenames:
                    continue
                prompt += f"{entity.role.value}: {entity.content}\n"

        if schema.model_id is not None:
            model = await self.prompt_repository.get(schema.model_id)
            prompt += model.text

            if schema.user_inputs and model.user_inputs:
                prompt_user_inputs_keys = [i.key for i in model.user_inputs]
                for user_input in schema.user_inputs:
                    if user_input.key in prompt_user_inputs_keys:
                        prompt = prompt.format(**{user_input.key: user_input.value})

        elif schema.user_prompt:
            prompt += schema.user_prompt

        return prompt

    async def _send(
        self, task_id: UUID, method: Coroutine[Any, Any, ExternalResponse]
    ) -> str | None:
        try:
            result = await method
        except Exception as e:
            logger.exception(e)
            await self.task_repository.update(task_id, error=str(e))
            return None

        self.remaining_tokens = result.remaining_tokens
        self.remaining_requests = result.remaining_requests
        self.remaining_reset_in = result.reset_in

        if result.content is None:
            await self.task_repository.update(task_id, error="Generation error")
            return None
        return result.content

    async def _send_for_image(
        self,
        task_id: UUID,
        context_id: UUID | None,
        method: Coroutine[Any, Any, ExternalResponse],
    ):
        content = await self._send(task_id, method)
        if content is None:
            return

        filename = str(task_id) + "-result"
        if not content.startswith("http"):
            self.storage_repository.store_file(filename, base64.b64decode(content))
            content = self.external_url + f"/api/task/{task_id}/result"

        await self.task_repository.create_items(
            TaskItem(task_id=task_id, result_url=content)
        )

        if context_id is None:
            return
        async with ContextService() as context_service:
            await context_service.add_entity_image(
                context_id, filename, ContextEntityRole.assistant
            )

    async def _send_for_text(
        self,
        task_id: UUID,
        context_id: UUID | None,
        method: Coroutine[Any, Any, ExternalResponse],
    ):
        content = await self._send(task_id, method)
        if content is None:
            return

        await self.task_repository.create_items(
            TaskItem(task_id=task_id, result_url=content)
        )

        if context_id is None:
            return
        async with ContextService() as context_service:
            await context_service.add_entity_text(
                context_id, content, ContextEntityRole.assistant
            )

    async def _send_2txt(
        self, task_id: UUID, schema: TaskTextCreateSchema, image: BytesIO | None = None
    ):
        request_input = []
        for context_entity in schema.context.entities if schema.context else []:
            if context_entity.content not in schema.context.images_filenames:
                request_input.append(
                    ExternalText2TextTaskSchema.TextMessage(
                        role=context_entity.role.value,
                        content=context_entity.content,
                    )
                )
                continue

            image_body = self.storage_repository.get_file(context_entity.content)
            if not image_body:
                continue
            request_input.append(
                ExternalText2TextTaskSchema.ImageMessage(
                    role=context_entity.role.value,
                    content=[
                        ExternalText2TextTaskSchema.ImageMessage.ImageContent(
                            image_url="data:image/png;base64,"
                            + base64.b64encode(image_body).decode()
                        )
                    ],
                )
            )

        if image is not None:
            request_input.append(
                ExternalText2TextTaskSchema.ImageMessage(
                    role=ContextEntityRole.user.value,
                    content=[
                        ExternalText2TextTaskSchema.ImageMessage.ImageContent(
                            image_url="data:image/png;base64,"
                            + base64.b64encode(image.getvalue()).decode()
                        )
                    ],
                )
            )

        prompt = await self.build_prompt(schema, include_context=False)
        request_input.append(
            ExternalText2TextTaskSchema.TextMessage(
                role=ContextEntityRole.user.value, content=prompt
            )
        )

        request = ExternalText2TextTaskSchema(input=request_input)
        await self._send_for_text(
            task_id,
            schema.context_id,
            self.external_repository.generate_text2text(request),
        )

    async def _send_txt2img(self, task_id: UUID, schema: TaskImageCreateSchema):
        prompt = await self.build_prompt(schema)
        request = ExternalText2ImageTaskSchema(
            prompt=prompt, size=schema.size, quality=schema.quality
        )
        images = []

        if schema.context is not None:
            for context_image_filename in schema.context.images_filenames:
                if not self.storage_repository.exists(context_image_filename):
                    continue
                context_image = BytesIO(
                    self.storage_repository.get_file(context_image_filename)
                )
                images.append(self._convert_image(context_image))

        if images:
            request = ExternalImage2ImageTaskSchema(
                prompt=prompt, size=schema.size, images=images, quality=schema.quality
            )
            return await self._send_for_image(
                task_id,
                schema.context_id,
                self.external_repository.generate_image2image(request),
            )
        return await self._send_for_image(
            task_id,
            schema.context_id,
            self.external_repository.generate_text2image(request),
        )

    async def _send_img2img(
        self, task_id: UUID, schema: TaskImageCreateSchema, image: BytesIO
    ):
        prompt = await self.build_prompt(schema)
        images = [self._convert_image(image)]

        if schema.context is not None:
            for context_image_filename in schema.context.images_filenames:
                if not self.storage_repository.exists(context_image_filename):
                    continue
                context_image = BytesIO(
                    self.storage_repository.get_file(context_image_filename)
                )
                images.append(self._convert_image(context_image))

        request = ExternalImage2ImageTaskSchema(
            prompt=prompt, size=schema.size, images=images, quality=schema.quality
        )
        return await self._send_for_image(
            task_id,
            schema.context_id,
            self.external_repository.generate_image2image(request),
        )

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema.model_validate(model)

    async def send_webhook(self, task_id: UUID, webhook_url: str):
        task = await self.get(task_id)
        async with ClientSession() as session:
            try:
                resp = await session.post(webhook_url, data=task.model_dump_json())
            except Exception as e:
                logger.warning(f"Error on webhook send: {e}")
                return
            if resp.status != 200:
                logger.warning(f"Error on webhook send: {await resp.text()}")

    @classmethod
    async def _process_request(
        cls,
        request_id: int,
        task_id: UUID,
        schema: str,
        image: BytesIO | None = None,
    ):
        async with cls() as self:
            logger.info(f"Sending {task_id=}")
            await self.request_repository.update(request_id, status="sended")
            await self.request_repository._commit()

            create_schema = json.loads(schema)

            try:
                if create_schema.get("task_type") == "image":
                    create_schema = TaskImageCreateSchema.model_validate(create_schema)
                    if image is not None:
                        await self._send_img2img(task_id, create_schema, image)
                    else:
                        await self._send_txt2img(task_id, create_schema)
                elif create_schema.get("task_type") == "text":
                    create_schema = TaskTextCreateSchema.model_validate(create_schema)
                    await self._send_2txt(task_id, create_schema, image)
                else:
                    await self.task_repository.update(task_id, error="Unknown task type")
            except Exception as e:
                await self.task_repository.update(task_id, error=str(e))

            await self.request_repository.delete(request_id)
            await self.task_repository._commit()
            if isinstance(create_schema, BaseModel) and create_schema.webhook_url is not None:
                await self.send_webhook(task_id, create_schema.webhook_url)
            elif isinstance(create_schema, dict) and create_schema.get("webhook_url"):
                await self.send_webhook(task_id, create_schema.get("webhook_url"))

        logger.info(f"Finished {task_id=}")

    async def add_request(
        self,
        task_id: UUID,
        schema: TaskImageCreateSchema | TaskTextCreateSchema,
        image: BytesIO | None = None,
    ):
        if schema.context_id is not None:
            try:
                prompt = await self.build_prompt(schema, include_context=False)
            except Exception as e:
                raise HTTPException(409, detail=str(e))

            async with ContextService() as context_service:
                if schema.context_id == "last":
                    schema.context_id = (
                        await context_service.get_last(schema.user_id)
                    ).id
                schema.context = await context_service.build_context(schema.context_id)

                await context_service.add_entity_text(
                    schema.context_id, prompt, ContextEntityRole.user
                )
                if image is not None:
                    await context_service.add_entity_image(
                        schema.context_id,
                        str(task_id) + "-request",
                        ContextEntityRole.user,
                    )

        await self.request_repository.create(
            task_id=task_id, schema=schema.model_dump_json()
        )
        if image is not None:
            self.storage_repository.store_file(
                str(task_id) + "-request", image.getvalue()
            )

    async def process_requests(self):
        sended_count = await self.request_repository.count(status="sended")
        if sended_count > 3:
            return
        requests = await self.request_repository.list(
            not_sended=True, count=3 - sended_count
        )
        tasks = []
        for request in requests:
            if request.task_id in self.sended_tasks:
                continue
            self.sended_tasks.append(request.task_id)
            image = None

            if self.storage_repository.exists(str(request.task_id) + "-request"):
                image = BytesIO(
                    self.storage_repository.get_file(str(request.task_id) + "-request")
                )

            asyncio.create_task(
                self._process_request(
                    request.id,
                    request.task_id,
                    request.schema,
                    image=image,
                )
            )

    def get_result(self, task_id: UUID) -> bytes:
        body = self.storage_repository.get_file(str(task_id) + "-result")
        if body is None:
            raise HTTPException(404)
        return body

    def get_statistics(self) -> TaskStatisticsSchema:
        if (
            self.remaining_requests is None
            or self.remaining_tokens is None
        ):
            raise HTTPException(
                500,
                detail="Remaining info is not stored. Please, wait for at least one request processed",
            )
        return TaskStatisticsSchema(
            remaining_requests=self.remaining_requests,
            remaining_tokens=self.remaining_tokens,
        )

    async def __aenter__(self):
        self.task_repository = await TaskRepository().__aenter__()
        self.prompt_repository = PromptRepository(session=self.task_repository.session)
        self.request_repository = TaskRequestRepository(
            session=self.task_repository.session
        )
        self.external_repository = OpenAIRepository()
        self.storage_repository = StorageRepository()
        return self

    async def __aexit__(self, *exinfo):
        await self.task_repository.__aexit__(*exinfo)
