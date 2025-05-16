from io import BytesIO
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.infrastructure.db.orm import ModelDB
from src.models.domain.entities import Model, ModelList
from src.models.domain.interfaces.model_repository import IModelRepository


class PGModelRepository(IModelRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_list(self, params: ModelList) -> list[Model]:
        query = select(ModelDB).offset(params.page * params.count).limit(params.count)
        query = query.options(selectinload(ModelDB.user_inputs))
        result = await self.session.scalars(query)
        return [
            self._to_domain(model)
            for model in result
        ]

    async def get_by_pk(self, pk: UUID) -> Model:
        model: ModelDB | None = await self.session.get(ModelDB, pk)
        if model is None:
            raise HTTPException(404)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ModelDB) -> Model:
        return Model(
            id=model.id,
            text=model.text,
            title=model.title,
            category_name=model.category_name,
            image=BytesIO(model.image.open().read()) if model.image else None
        )
