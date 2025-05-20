from uuid import UUID
from src.models.domain.dtos import ModelListParamsDTO
from src.models.domain.entities import ModelCategory, ModelList
from src.models.domain.interfaces.model_uow import IModelUnitOfWork


async def get_model_categories_list(
    params: ModelListParamsDTO, uow: IModelUnitOfWork
) -> list[ModelCategory]:
    repository_params = ModelList(**params.model_dump())
    async with uow:
        models = await uow.model_categories.get_list(repository_params)
    return models


async def get_model_category(category_id: UUID, uow: IModelUnitOfWork) -> ModelCategory:
    async with uow:
        model = await uow.model_categories.get_by_pk(category_id)
    return model
