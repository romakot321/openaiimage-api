from io import BytesIO
from uuid import UUID

from fastapi import HTTPException

from src.models.domain.interfaces.model_uow import IModelUnitOfWork


async def get_model_image(model_id: UUID, uow: IModelUnitOfWork) -> BytesIO:
    async with uow:
        model = await uow.models.get_by_pk(model_id)
    if model.image is None:
        raise HTTPException(404)
    return model.image
