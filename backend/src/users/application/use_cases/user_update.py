from uuid import UUID

from src.users.domain.entities import User
from src.users.domain.interfaces.user_uow import IUserUnitOfWork


async def update_user(pk: UUID, user_data: , uow: IUserUnitOfWork) -> User:
    async with uow:
        user = await uow.users.update_by_pk(pk)
