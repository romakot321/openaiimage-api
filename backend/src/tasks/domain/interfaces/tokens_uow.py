import abc
from uuid import UUID

from src.users.domain.interfaces.user_repository import IUserRepository


class ITokensUnitOfWork(abc.ABC):
    users: IUserRepository

    @abc.abstractmethod
    async def write_off_tokens(self, external_user_id: str, app_bundle: str, value: int) -> None: ...

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
