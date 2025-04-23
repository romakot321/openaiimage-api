from uuid import UUID
from fastapi import Depends

from app.db.tables import TaskItem
from app.repositories.external import ExternalRepository
from app.repositories.task import TaskRepository
from app.schemas.external import ExternalTaskSchema
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskSearchSchema, TaskShortSchema, TaskUpdateSchema


class TaskService:
    def __init__(
            self,
            task_repository: TaskRepository = Depends(TaskRepository.depend),
            external_repository: ExternalRepository = Depends()
    ):
        self.task_repository = task_repository
        self.external_repository = external_repository

    async def create(self, schema: TaskCreateSchema) -> TaskSchema:
        model = await self.task_repository.create(**schema.model_dump())
        return TaskSchema.model_validate(model)

    async def send(self, task_id: UUID, schema: TaskCreateSchema):
        request = ExternalTaskSchema(text=schema.text)
        external_task_id = await self.external_repository.create_task(request)

        response = None
        for _ in range(6):
            external_task = await self.external_repository.get_task(external_task_id)
            if external_task:
                response = external_task
                break

        if response is None:
            return await self.task_repository.update(task_id, error="Timeout")
        return await self.task_repository.create_items(TaskItem(task_id=task_id))

    async def get(self, task_id: UUID) -> TaskSchema:
        model = await self.task_repository.get(task_id)
        return TaskSchema.model_validate(model)

    async def update(self, task_id: UUID, schema: TaskUpdateSchema) -> TaskSchema:
        model = await self.task_repository.update(task_id, **schema.model_dump())
        return TaskSchema.model_validate(model)

    async def delete(self, task_id: UUID) -> None:
        await self.task_repository.delete(task_id)

    async def get_list(self, schema: TaskSearchSchema) -> list[TaskShortSchema]:
        models = await self.task_repository.list(**schema.model_dump(exclude_none=True))
        return [
            TaskShortSchema.model_validate(model)
            for model in models
        ]
