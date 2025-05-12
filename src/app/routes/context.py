from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.routes import validate_api_token
from app.schemas.context import ContextCreateSchema, ContextSchema
from app.services.context import ContextService


router = APIRouter(prefix="/api/context", tags=["Context"])


@router.post(
    "", response_model=ContextSchema, dependencies=[Depends(validate_api_token)]
)
async def create_new_context(
    schema: ContextCreateSchema, context_service: ContextService = Depends()
):
    return await context_service.create(schema)


@router.get(
    "/{context_id}",
    response_model=ContextSchema,
    dependencies=[Depends(validate_api_token)],
)
async def get_context(context_id: UUID, context_service: ContextService = Depends()):
    return await context_service.get(context_id)


@router.delete(
    "/{context_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_api_token)],
)
async def delete_context(context_id: UUID, context_service: ContextService = Depends()):
    await context_service.delete(context_id)
