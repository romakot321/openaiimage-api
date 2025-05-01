from contextlib import suppress
from fastapi import Response, HTTPException
from loguru import logger
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService as BaseRepository

from app.db.tables import TaskRequest, engine


class TaskRequestRepository[Table: TaskRequest, int](BaseRepository):
    base_table = TaskRequest
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

    async def create(self, **fields) -> TaskRequest:
        return await self._create(**fields)

    async def list(self, not_sended: bool | None = None, page=None, count=None) -> list[TaskRequest]:
        query = self._get_list_query(page=page, count=count)
        if not_sended:
            query = query.filter(TaskRequest.status == None)
        query = query.order_by(TaskRequest.created_at.asc())
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: int) -> TaskRequest:
        return await self._get_one(
            id=model_id,
        )

    async def update(self, model_id: int, **fields) -> TaskRequest:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self, status: str | None = None):
        return await self._count(status=status)

