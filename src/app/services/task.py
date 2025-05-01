from io import BytesIO
import asyncio
from typing import Coroutine
from PIL import Image
from loguru import logger
from uuid import UUID
from fastapi import Depends, HTTPException
import base64
import os

from app.db.tables import TaskItem
from app.repositories.openai import OpenAIRepository
from app.repositories.prompt import PromptRepository
from app.repositories.task import TaskRepository
from app.repositories.task_request import TaskRequestRepository
from app.schemas.external import (
    ExternalImage2ImageTaskSchema,
    ExternalText2ImageTaskSchema,
)
from app.repositories.storage import StorageRepository
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskShortSchema


class TaskService:
    external_url = os.getenv("EXTERNAL_URL")

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
        self.task_repository = task_repository
        self.external_repository = openai_repository
        self.prompt_repository = prompt_repository
        self.request_repository = request_repository
        self.storage_repository = storage_repository

    async def create(self, schema: TaskCreateSchema) -> TaskShortSchema:
        if schema.user_prompt is None and schema.model_id is None:
            raise HTTPException(
                422, detail="Model id and prompt cannot be None at one time"
            )
        model = await self.task_repository.create(
            user_id=schema.user_id, app_bundle=schema.app_bundle
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

    async def build_prompt(self, schema: TaskCreateSchema) -> str:
        prompt = ""

        if schema.model_id is not None:
            model = await self.prompt_repository.get(schema.model_id)
            prompt += model.text

            if schema.user_inputs and prompt.user_inputs:
                prompt_user_inputs_keys = [i.key for i in prompt.user_inputs]
                for user_input in schema.user_inputs:
                    if user_input.key in prompt_user_inputs_keys:
                        prompt = prompt.format(**{user_input.key: user_input.value})

        elif schema.user_prompt:
            prompt = schema.user_prompt

        return prompt

    async def _send(self, task_id: UUID, method: Coroutine):
        try:
            result = await method
        except Exception as e:
            logger.exception(e)
            return await self.task_repository.update(task_id, error=str(e))

        if result is None:
            return await self.task_repository.update(task_id, error="Generation error")
        if not result.startswith("http"):
            self.storage_repository.store_file(str(task_id), base64.b64decode(result))
            result = self.external_url + f"/api/task/{task_id}/result"

        await self.task_repository.create_items(
            TaskItem(task_id=task_id, result_url=result)
        )

    async def send_txt2img(self, task_id: UUID, schema: TaskCreateSchema):
        print("txt2img")
        prompt = await self.build_prompt(schema)
        request = ExternalText2ImageTaskSchema(
            prompt=prompt, size=schema.size, quality=schema.quality
        )
        return await self._send(
            task_id, self.external_repository.generate_text2image(request)
        )

    async def send_img2img(
        self, task_id: UUID, schema: TaskCreateSchema, image: BytesIO
    ):
        print("img2img")
        prompt = await self.build_prompt(schema)
        image = self._convert_image(image)
        request = ExternalImage2ImageTaskSchema(
            prompt=prompt, size=schema.size, image=image, quality=schema.quality
        )
        return await self._send(
            task_id, self.external_repository.generate_image2image(request)
        )

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema.model_validate(model)

    @classmethod
    async def _process_request(
        cls,
        request_id: int,
        task_id: UUID,
        schema: TaskCreateSchema,
        image: BytesIO | None = None,
    ):
        async with cls() as self:
            logger.info(f"Sending {task_id=}")
            await self.request_repository.update(request_id, status="sended")

            if image is not None:
                self.storage_repository.delete_file(str(task_id))
                await self.send_img2img(task_id, schema, image)
            else:
                await self.send_txt2img(task_id, schema)

            await self.request_repository.delete(request_id)
            logger.info(f"Finished {task_id=}")

    async def add_request(
        self, task_id: UUID, schema: TaskCreateSchema, image: BytesIO | None = None
    ):
        await self.request_repository.create(
            task_id=task_id, schema=schema.model_dump_json()
        )
        if image is not None:
            self.storage_repository.store_file(str(task_id), image.getvalue())

    async def process_requests(self):
        sended_count = await self.request_repository.count(status="sended")
        if sended_count > 8:
            return
        requests = await self.request_repository.list(
            not_sended=True, count=8 - sended_count
        )
        tasks = []
        for request in requests:
            image = None

            if self.storage_repository.exists(str(request.task_id)):
                image = BytesIO(self.storage_repository.get_file(str(request.task_id)))

            asyncio.create_task(
                self._process_request(
                    request.id,
                    request.task_id,
                    TaskCreateSchema.model_validate_json(request.schema),
                    image=image,
                )
            )

    async def __aenter__(self):
        self.task_repository = await TaskRepository().__aenter__()
        self.prompt_repository = PromptRepository(
            session = self.task_repository.session
        )
        self.request_repository = TaskRequestRepository(
            session = self.task_repository.session
        )
        self.external_repository = OpenAIRepository()
        self.storage_repository = StorageRepository()
        return self

    async def __aexit__(self, *exinfo):
        await self.task_repository.__aexit__(*exinfo)

    def get_result(self, task_id: UUID) -> bytes:
        return self.storage_repository.get_file(str(task_id))
