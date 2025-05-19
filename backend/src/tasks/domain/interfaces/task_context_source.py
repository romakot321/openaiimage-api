import abc
from typing import Generic, TypeVar
from uuid import UUID

TContextMessage = TypeVar("TContextMessage")


class ITaskContextSource(abc.ABC, Generic[TContextMessage]):
    @abc.abstractmethod
    async def get_task_context(self, context_id: UUID | str, user_id: str | None = None) -> list[TContextMessage]: ...

    @abc.abstractmethod
    async def append_task_context(self, context_id: UUID | str, messages: list[TContextMessage], user_id: str | None = None) -> None: ...

    @abc.abstractmethod
    async def get_task_context_left(self, context_id: UUID | str, user_id: str | None = None) -> dict: ...
