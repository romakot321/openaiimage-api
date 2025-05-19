from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.contexts.domain.dtos import ContextUsageDTO
from src.contexts.domain.entities import (
    ContextEntity,
    ContextEntityContentType,
    ContextEntityCreate,
    ContextEntityRole,
)
from src.contexts.domain.interfaces.context_entity_repository import (
    IContextEntityRepository,
)
from src.contexts.infrastructure.db.orm import ContextEntityDB
from src.contexts.infrastructure.db.orm import ContextDB
from src.contexts.domain.entities import Context, ContextCreate
from src.contexts.domain.interfaces.context_repository import IContextRepository


class PGContextRepository(IContextRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create(self, task: ContextCreate) -> Context:
        model = ContextDB(**task.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.commit()
        except IntegrityError as e:
            try:
                detail = "Context can't be created. " + str(e)
            except IndexError:
                detail = "Context can't be created due to integrity error."
            raise HTTPException(409, detail=detail)

        return Context(id=model.id, user_id=model.user_id, entities=[], tasks=[])

    async def get_by_pk(self, pk: UUID) -> Context:
        model: ContextDB | None = await self.session.get(
            ContextDB,
            pk,
            options=[selectinload(ContextDB.entities), selectinload(ContextDB.tasks)],
        )
        if model is None:
            raise HTTPException(404)
        return self._to_domain(model)

    async def delete_by_pk(self, pk: UUID) -> None:
        query = delete(ContextDB).filter_by(id=pk)
        await self.session.execute(query)

    async def get_user_last(self, user_id: str) -> Context:
        query = (
            select(ContextDB)
            .filter_by(user_id=user_id)
            .order_by(ContextDB.created_at.desc())
            .limit(1)
        )
        model = await self.session.scalar(query)
        if model is None:
            raise HTTPException(404)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ContextDB) -> Context:
        return Context(
            id=model.id,
            user_id=model.user_id,
            entities=model.entities,
            tasks=model.tasks,
        )


class PGContextEntityRepository(IContextEntityRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create(self, task: ContextEntityCreate) -> ContextEntity:
        model = ContextEntityDB(**task.model_dump(mode="json"))
        self.session.add(model)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Context can't be created. " + str(e)
            except IndexError:
                detail = "Context can't be created due to integrity error."
            raise HTTPException(409, detail=detail)

        return self._to_domain(model)

    async def get_list_by_context_id(self, context_id: UUID) -> list[ContextEntity]:
        query = select(ContextEntityDB).filter_by(context_id=context_id)
        query = query.order_by(ContextEntityDB.created_at.desc())
        result = await self.session.scalars(query)
        return [self._to_domain(model) for model in result]

    async def delete_by_pk(self, pk: UUID) -> None:
        query = delete(ContextEntityDB).filter_by(id=pk)
        await self.session.execute(query)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "Context can't be deleted. " + str(e)
            except IndexError:
                detail = "Context can't be deleted due to integrity error."
            raise HTTPException(409, detail=detail)

    async def get_context_usage(self, context_id: UUID) -> ContextUsageDTO:
        return ContextUsageDTO(
            id=context_id,
            text_used=await self._get_context_text_usage(context_id) or 0,
            images_used=await self._get_context_images_usage(context_id) or 0,
        )

    async def _get_context_images_usage(self, context_id: UUID) -> int | None:
        query = (
            select(func.count(ContextEntityDB.id))
            .select_from(ContextEntityDB)
            .filter_by(
                context_id=context_id, content_type=ContextEntityContentType.image
            )
        )
        result = await self.session.execute(query)
        context_image_usage = result.fetchone()
        if context_image_usage is not None:
            return context_image_usage._tuple()[0]

    async def _get_context_text_usage(self, context_id: UUID) -> int | None:
        query = select(func.sum(func.char_length(ContextEntityDB.content))).filter_by(
            context_id=context_id, content_type=ContextEntityContentType.text
        )
        result = await self.session.execute(query)
        context_text_usage = result.fetchone()
        if context_text_usage is not None:
            return context_text_usage._tuple()[0]

    @staticmethod
    def _to_domain(model: ContextEntityDB) -> ContextEntity:
        return ContextEntity(
            id=model.id,
            content_type=model.content_type,
            content=model.content,
            role=ContextEntityRole(model.role),
            context_id=UUID(model.context_id),
        )
