from io import BytesIO
import asyncio
from typing import Coroutine
from PIL import Image
from loguru import logger
from uuid import UUID
from fastapi import Depends, HTTPException

from app.db.tables import TaskItem
from app.repositories.openai import OpenAIRepository
from app.repositories.external import ExternalRepository
from app.repositories.prompt import PromptRepository
from app.repositories.task import TaskRepository
from app.schemas.external import (
    ExternalImage2ImageTaskSchema,
    ExternalText2ImageTaskSchema,
)
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskShortSchema


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository = Depends(TaskRepository.depend),
        prompt_repository: PromptRepository = Depends(PromptRepository.depend),
        external_repository: ExternalRepository = Depends(),
        # openai_repository: OpenAIRepository = Depends()
    ):
        self.task_repository = task_repository
        self.external_repository = external_repository
        self.prompt_repository = prompt_repository

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
        image = image.convert("RGBA")
        [
            image.putpixel((x, y), image.getpixel((x, y))[:3] + (0,))
            for x in range(image.size[0])
            for y in range(image.size[1])
        ]
        logger.debug(image.getpixel((0, 0)))
        image.save(converted, format="PNG", mode="RGBA")
        converted.seek(0)
        converted.name = "tmp.png"
        return converted

    async def build_prompt(self, schema: TaskCreateSchema) -> str:
        prompt = ""

        if schema.model_id is not None:
            model = await self.prompt_repository.get(schema.model_id)
            prompt += model.text
            if schema.user_prompt is not None and "{user_prompt}" in prompt:
                prompt = prompt.format(user_prompt=schema.user_prompt)
        elif schema.user_prompt:
            prompt = schema.user_prompt

        return prompt

    async def _send(self, task_id: UUID, method: Coroutine):
        try:
            external_task_id = await method
        except Exception as e:
            logger.exception(e)
            return await self.task_repository.update(task_id, error=str(e))

        if task_id is None:
            return await self.task_repository.update(task_id, error="Generation error")

        for _ in range(12):
            await asyncio.sleep(5)
            external_task = await self.external_repository.get_image_generation(
                external_task_id
            )
            if external_task.is_finished or external_task.is_invalid:
                break

        if not external_task.is_finished:
            await self.task_repository.update(task_id, error="Timeout")
        elif external_task.is_invalid:
            await self.task_repository.update(task_id, error=external_task.comment)
        else:
            await self.task_repository.create_items(
                TaskItem(task_id=task_id, result_url=external_task.image_url)
            )

    async def send_img2img(
        self, task_id: UUID, schema: TaskCreateSchema, image: BytesIO
    ):
        prompt = await self.build_prompt(schema)
        image = self._convert_image(image)

        method = self.external_repository.start_image2image_generate(
            prompt, image, schema.size.value
        )
        await self._send(task_id, method)

    async def send_txt2img(self, task_id: UUID, schema: TaskCreateSchema):
        prompt = await self.build_prompt(schema)

        method = self.external_repository.start_image_generate(
            prompt, schema.size.value
        )
        await self._send(task_id, method)

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema.model_validate(model)
