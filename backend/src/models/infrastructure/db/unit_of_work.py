from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.models.domain.interfaces.model_uow import IModelUnitOfWork

from backend.src.models.infrastructure.db.repositories import PGModelRepository
from src.db.engine import async_session_maker


class PGModelUnitOfWork(IModelUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.models = PGModelRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()
