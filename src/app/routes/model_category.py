from fastapi import APIRouter, Depends, Response
from uuid import UUID

from app.routes import validate_api_token
from app.schemas.model import ModelCategorySearchSchema, ModelCategorySchema
from app.services.model import ModelCategoryService

router = APIRouter(prefix="/api/model", tags=["ModelCategory"])


@router.get(
    "",
    response_model=list[ModelCategorySchema],
    dependencies=[Depends(validate_api_token)],
)
async def get_categories_list(
    schema: ModelCategorySearchSchema = Depends(),
    service: ModelCategoryService = Depends(),
):
    return await service.get_list(schema)


@router.get(
    "/{model_category_id}",
    response_model=ModelCategorySchema,
    dependencies=[Depends(validate_api_token)],
)
async def get_category(
    model_category_id: UUID, service: ModelCategoryService = Depends()
):
    return await service.get(model_category_id)
