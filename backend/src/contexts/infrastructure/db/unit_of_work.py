from sqlalchemy.ext.asyncio import AsyncSession
from src.tasks.domain.interfaces.task_uow import IContextUnitOfWork

from src.db.engine import async_session_maker
from src.contexts.infrastructure.db.repositories import PGContextEntityRepository, PGContextRepository


class PGContextUnitOfWork(IContextUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.contexts = PGContextRepository(self.session)
        self.context_entity = PGContextEntityRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()
