import abc
from uuid import UUID

from backend.src.contexts.domain.dtos import ContextUsageDTO
from src.contexts.domain.entities import Context, ContextEntity, ContextEntityCreate


class IContextEntityRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, task: ContextEntityCreate) -> ContextEntity: ...

    @abc.abstractmethod
    async def get_list_by_context_id(self, context_id: UUID) -> list[ContextEntity]: ...

    @abc.abstractmethod
    async def get_context_usage(self, context_id: UUID) -> ContextUsageDTO: ...
