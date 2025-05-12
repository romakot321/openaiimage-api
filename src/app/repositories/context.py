from contextlib import suppress
from fastapi import Response, HTTPException
from loguru import logger
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService as BaseRepository
from uuid import UUID

from app.db.tables import Context, Task, engine


class ContextRepository[Table: Context, int](BaseRepository):
    base_table = Context
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

    async def create(self, **fields) -> Context:
        return await self._create(**fields)

    async def list(self, page=None, count=None) -> list[Context]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: UUID) -> Context:
        return await self._get_one(
            id=model_id,
            select_in_load=[Context.entities, {"parent": Context.tasks, "children": [Task.items]}]
        )

    async def get_last(self, user_id: str) -> Context:
        query = select(Context).filter_by(user_id=user_id).order_by(Context.created_at.desc()).limit(1)
        model = await self.session.scalar(query)
        if model is None:
            raise HTTPException(404)
        return model

    async def update(self, model_id: UUID, **fields) -> Context:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: UUID):
        await self._delete(model_id)

    async def count(self):
        return await self._count()

