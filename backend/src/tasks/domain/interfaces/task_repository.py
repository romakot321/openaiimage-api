import abc
from uuid import UUID

from src.tasks.domain.entities import TaskCreate, TaskUpdate, Task


class ITaskRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, task: TaskCreate) -> Task: ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> Task: ...

    @abc.abstractmethod
    async def update(self, pk: UUID, task: TaskUpdate) -> None: ...
