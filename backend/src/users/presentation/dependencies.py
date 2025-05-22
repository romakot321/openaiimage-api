from typing import Annotated
from fastapi import Depends
from src.tasks.domain.interfaces.tokens_uow import ITokensUnitOfWork
from src.users.domain.interfaces.user_uow import IUserUnitOfWork
from src.users.infrastructure.db.tokens_uow import PGTokensUnitOfWork
from src.users.infrastructure.db.unit_of_work import PGUserUnitOfWork


def get_user_uow() -> IUserUnitOfWork:
    return PGUserUnitOfWork()


def get_tokens_uow() -> ITokensUnitOfWork:
    return PGTokensUnitOfWork()


UserUoWDepend = Annotated[IUserUnitOfWork, Depends(get_user_uow)]
