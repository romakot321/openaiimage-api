from io import BytesIO
from loguru import logger
from uuid import UUID
from fastapi import Depends, HTTPException

from app.db.tables import TaskItem
from app.repositories.openai import OpenAIRepository
from app.repositories.prompt import PromptRepository
from app.repositories.task import TaskRepository
from app.schemas.external import ExternalTaskSchema
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskShortSchema


class TaskService:
    def __init__(
            self,
            task_repository: TaskRepository = Depends(TaskRepository.depend),
            prompt_repository: PromptRepository = Depends(PromptRepository.depend),
            openai_repository: OpenAIRepository = Depends()
    ):
        self.task_repository = task_repository
        self.external_repository = openai_repository
        self.prompt_repository = prompt_repository

    async def create(self, schema: TaskCreateSchema) -> TaskShortSchema:
        if schema.prompt is None and schema.model_id is None:
            raise HTTPException(422, detail="Model id and prompt cannot be None at one time")
        model = await self.task_repository.create(user_id=schema.user_id, app_bundle=schema.app_bundle)
        return TaskShortSchema.model_validate(model)

    async def send(self, task_id: UUID, schema: TaskCreateSchema, image: BytesIO):
        prompt = schema.prompt or ""

        if schema.model_id is not None:
            prompt += await self.prompt_repository.get(schema.model_id)
        request = ExternalTaskSchema(prompt=prompt, size=schema.size, image=image)

        try:
            result_url = await self.external_repository.generate_image2image(request)
        except Exception as e:
            logger.exception(e)
            return await self.task_repository.update(task_id, error=str(e))
        logger.debug(result_url)

        if result_url is None:
            return await self.task_repository.update(task_id, error="Generation error")
        await self.task_repository.create_items(TaskItem(task_id=task_id, result_url=result_url))

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema.model_validate(model)
