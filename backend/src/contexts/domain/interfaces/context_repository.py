import abc
from uuid import UUID

from src.contexts.domain.entities import ContextCreate, Context


class IContextRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, task: ContextCreate) -> Context: ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> Context: ...

    @abc.abstractmethod
    async def delete_by_pk(self, pk: UUID) -> None: ...
