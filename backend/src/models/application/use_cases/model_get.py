from uuid import UUID
from backend.src.models.domain.dtos import ModelListParamsDTO
from backend.src.models.domain.entities import Model, ModelList
from backend.src.models.domain.interfaces.model_uow import IModelUnitOfWork


async def get_models_list(
    params: ModelListParamsDTO, uow: IModelUnitOfWork
) -> list[Model]:
    repository_params = ModelList(**params.model_dump())
    async with uow:
        models = await uow.models.get_list(repository_params)
    return models


async def get_model(model_id: UUID, uow: IModelUnitOfWork) -> Model:
    async with uow:
        model = await uow.models.get_by_pk(model_id)
    return model
