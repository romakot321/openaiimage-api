from fastapi import APIRouter, Depends, Response
from uuid import UUID

from app.routes import validate_api_token
from app.schemas.model import ModelSearchSchema, ModelSchema
from app.services.model import ModelService

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.get(
    "",
    response_model=list[ModelSchema],
    dependencies=[Depends(validate_api_token)]
)
async def list_models(
        schema: ModelSearchSchema = Depends(),
        service: ModelService = Depends()
):
    return await service.list(schema)


@router.get(
    "/{model_id}/image",
    response_class=Response
)
async def get_model_image(model_id: UUID, service: ModelService = Depends()):
    image = await service.get_image(model_id)
    return Response(content=image, media_type="image/png")
