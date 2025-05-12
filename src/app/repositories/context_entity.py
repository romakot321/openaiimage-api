from contextlib import suppress
from fastapi import Response, HTTPException
from loguru import logger
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService as BaseRepository
from uuid import UUID

from app.db.tables import ContextEntity, ContextEntityItem, engine


class ContextEntityRepository[Table: ContextEntity, int](BaseRepository):
    base_table = ContextEntity
    engine = engine
    session: AsyncSession
    response: Response

    async def _commit(self, force: bool = False):
        """
        Commit changes.
        Handle sqlalchemy.exc.IntegrityError.
        If exception is not found error,
        then throw HTTPException with 404 status (Not found).
        Else log exception and throw HTTPException with 409 status (Conflict)
        """
        try:
            await self.session.commit()
        except exc.IntegrityError as e:
            await self.session.rollback()
            if 'is not present in table' not in str(e.orig):
                logger.exception(e)
                raise HTTPException(status_code=409)
            table_name = str(e.orig).split('is not present in table')[1]
            table_name = table_name.strip().capitalize()
            table_name = table_name.strip('"').strip("'")
            raise HTTPException(
                status_code=404,
                detail=f'{table_name} not found'
            )

    async def create(self, **fields) -> ContextEntity:
        return await self._create(**fields)

    async def list(self, context_id: str | UUID | None = None, page=None, count=None) -> list[ContextEntity]:
        return list(await self._get_list(context_id=context_id, page=page, count=count))

    async def get(self, model_id: UUID) -> ContextEntity:
        return await self._get_one(
            id=model_id,
        )

    async def update(self, model_id: UUID, **fields) -> ContextEntity:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

    async def count(self):
        return await self._count()

