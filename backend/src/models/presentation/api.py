from uuid import UUID
from fastapi import APIRouter
from fastapi.responses import Response

from backend.src.models.domain.dtos import ModelListParamsDTO, ModelReadDTO
from backend.src.models.presentation.dependencies import ModelUoWDepend
from src.models.application.use_cases.model_get import get_models_list
from src.models.application.use_cases.model_image import get_model_image as uc_get_model_image

router = APIRouter()


@router.get("", response_model=list[ModelReadDTO])
async def list_models(params: ModelListParamsDTO, uow: ModelUoWDepend):
    return await get_models_list(params, uow)


@router.get("/{model_id}/image", response_class=Response)
async def get_model_image(model_id: UUID, uow: ModelUoWDepend):
    buffer = await uc_get_model_image(model_id, uow)
    return Response(content=buffer.getvalue(), media_type="image/png")
