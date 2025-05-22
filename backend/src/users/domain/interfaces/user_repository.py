import abc
from uuid import UUID

from src.users.domain.entities import UserCreate, UserUpdate
from src.users.domain.entities import User


class IUserRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> User: ...

    @abc.abstractmethod
    async def create(self, user_data: UserCreate) -> User: ...

    @abc.abstractmethod
    async def update_by_pk(self, pk: UUID, user_data: UserUpdate) -> User: ...

    @abc.abstractmethod
    async def get_by_external(self, external_id: str, app_bundle: str) -> User: ...
