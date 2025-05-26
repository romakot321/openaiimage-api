from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.infrastructure.db.orm import UserDB
from src.users.domain.entities import User, UserCreate, UserUpdate
from src.users.domain.interfaces.user_repository import IUserRepository


class PGUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_pk(self, pk: UUID) -> User:
        user: UserDB | None = await self.session.get(UserDB, pk)
        if user is None:
            raise HTTPException(404)
        return self._to_domain(user)

    async def create(self, user_data: UserCreate) -> User:
        user = UserDB(**user_data.model_dump(exclude_unset=True))
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError as e:
            detail = "User can't be created. " + str(e)
            raise HTTPException(409, detail=detail)

        return self._to_domain(user)

    async def update_by_external(self, external_id: str, app_bundle: str, user_data: UserUpdate) -> User:
        query = (
            update(UserDB)
            .values(**user_data.model_dump(exclude_unset=True))
            .filter_by(external_id=external_id, app_bundle=app_bundle)
        )
        await self.session.execute(query)

        try:
            await self.session.flush()
        except IntegrityError as e:
            detail = "User can't be updated. " + str(e)
            raise HTTPException(409, detail=detail)

        return await self.get_by_external(external_id, app_bundle)

    async def update_by_pk(self, pk: UUID, user_data: UserUpdate) -> User:
        query = (
            update(UserDB)
            .values(**user_data.model_dump(exclude_unset=True))
            .filter_by(id=pk)
        )
        await self.session.execute(query)

        try:
            await self.session.flush()
        except IntegrityError as e:
            detail = "User can't be updated. " + str(e)
            raise HTTPException(409, detail=detail)

        return await self.get_by_pk(pk)

    async def get_by_external(self, external_id: str, app_bundle: str) -> User:
        query = select(UserDB).filter_by(external_id=external_id, app_bundle=app_bundle)
        user = await self.session.scalar(query)
        if user is None:
            raise HTTPException(404)
        return self._to_domain(user)

    @staticmethod
    def _to_domain(user: UserDB) -> User:
        return User(
            id=user.id,
            external_id=user.external_id,
            app_bundle=user.app_bundle,
            tokens=user.tokens,
        )
