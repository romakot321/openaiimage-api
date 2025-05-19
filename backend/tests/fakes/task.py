from uuid import UUID, uuid4
from fastapi import HTTPException
from src.tasks.domain.entities import Task, TaskCreate, TaskUpdate
from src.tasks.domain.interfaces.task_repository import ITaskRepository
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


class FakeTaskRepository(ITaskRepository):
    def __init__(self):
        self._tasks = []
        self._last_task_id = 0

    async def create(self, task: TaskCreate) -> Task:
        user = Task(id=self._get_new_task_id(), **task.model_dump())
        self._tasks.append(user)
        return user

    async def get_by_pk(self, pk: UUID) -> Task:
        for task in self._tasks:
            if task.id == pk:
                return task

        raise HTTPException(404)

    async def update(self, pk: UUID, task: TaskUpdate) -> None:
        model = await self.get_by_pk(pk)
        for field, value in task.model_dump(exclude_unset=True).items():
            setattr(model, field, value)

    def _get_new_task_id(self) -> UUID:
        return uuid4()


class FakeTaskUnitOfWork(ITaskUnitOfWork):
    tasks: ITaskRepository

    def __init__(self):
        self.tasks = FakeTaskRepository()
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def _rollback(self):
        pass
