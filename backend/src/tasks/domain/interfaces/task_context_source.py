import abc
from typing import Generic, TypeVar
from uuid import UUID

TContextMessage = TypeVar("TContextMessage")


class ITaskContextSource(abc.ABC, Generic[TContextMessage]):
    @abc.abstractmethod
    async def get_task_context(self, context_id: UUID) -> list[TContextMessage]: ...

    @abc.abstractmethod
    async def append_task_context(self, context_id: UUID, message: TContextMessage) -> None: ...

    @abc.abstractmethod
    async def get_task_context_left(self, context_id: UUID) -> dict: ...
