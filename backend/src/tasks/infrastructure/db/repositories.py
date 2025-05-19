from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.domain.interfaces.task_item_repository import ITaskItemRepository
from src.tasks.infrastructure.db.orm import TaskDB, TaskItemDB
from src.tasks.domain.entities import Task, TaskCreate, TaskItem, TaskItemCreate, TaskUpdate
from src.tasks.domain.interfaces.task_repository import ITaskRepository


class PGTaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create(self, task: TaskCreate) -> Task:
        model = TaskDB(**task.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Task can't be created. " + str(e)
            except IndexError:
                detail = "Task can't be created due to integrity error."
            raise HTTPException(409, detail=detail)

        return Task(
            id=model.id,
            user_id=model.user_id,
            app_bundle=model.app_bundle,
            context_id=model.context_id,
            error=model.error,
            items=[]
        )

    async def get_by_pk(self, pk: UUID) -> Task:
        model: TaskDB | None = await self.session.get(TaskDB, pk)
        if model is None:
            raise HTTPException(404)
        return self._to_domain(model)

    async def update(self, pk: UUID, task: TaskUpdate) -> None:
        query = update(TaskDB).filter_by(id=pk).values(**task.model_dump(mode="json", exclude_none=True))
        await self.session.execute(query)
        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Task can't be updated. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "Task can't be updated due to integrity error."
            raise HTTPException(409, detail=detail)

    @staticmethod
    def _to_domain(model: TaskDB) -> Task:
        return Task(
            id=model.id,
            user_id=model.user_id,
            app_bundle=model.app_bundle,
            context_id=model.context_id,
            error=model.error,
            items=model.items
        )


class PGTaskItemRepository(ITaskItemRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create(self, task_item: TaskItemCreate) -> TaskItem:
        model = TaskItemDB(**task_item.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "TaskItem can't be created. " + str(e)
            except IndexError:
                detail = "TaskItem can't be created due to integrity error."
            raise HTTPException(409, detail=detail)

        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: TaskItemDB) -> TaskItem:
        return TaskItem(id=model.id, result_url=model.result_url)
