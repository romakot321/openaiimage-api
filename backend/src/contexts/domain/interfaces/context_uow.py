import abc

from src.contexts.domain.interfaces.context_entity_repository import IContextEntityRepository
from src.contexts.domain.interfaces.context_repository import IContextRepository


class IContextUnitOfWork(abc.ABC):
    contexts: IContextRepository
    context_entity: IContextEntityRepository

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _rollback(self):
        pass

    @abc.abstractmethod
    async def _commit(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self._rollback()
