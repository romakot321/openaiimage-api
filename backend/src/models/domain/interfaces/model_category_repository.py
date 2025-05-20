import abc
from uuid import UUID

from src.models.domain.entities import ModelCategory, ModelList


class IModelCategoryRepository(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, params: ModelList) -> list[ModelCategory]: ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> ModelCategory: ...
