import abc

from src.users.domain.interfaces.user_repository import IUserRepository


class IUserUnitOfWork(abc.ABC):
    users: IUserRepository

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
