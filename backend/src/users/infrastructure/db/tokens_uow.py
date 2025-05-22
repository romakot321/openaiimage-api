from src.tasks.domain.interfaces.tokens_uow import ITokensUnitOfWork
from src.users.domain.entities import UserUpdate
from src.users.infrastructure.db.repositories import PGUserRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import async_session_maker


class PGTokensUnitOfWork(ITokensUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    async def write_off_tokens(self, external_user_id: str, app_bundle: str, value: int) -> None:
        user = await self.users.get_by_external(external_user_id, app_bundle)
        await self.users.update_by_pk(user.id, UserUpdate(tokens=user.tokens - value))

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = PGUserRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()

