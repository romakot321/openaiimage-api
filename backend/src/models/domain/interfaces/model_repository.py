import abc
from uuid import UUID

from backend.src.models.domain.entities import Model, ModelList


class IModelRepository(abc.ABC):
    @abc.abstractmethod
    async def get_list(self, params: ModelList) -> list[Model]: ...

    @abc.abstractmethod
    async def get_by_pk(self, pk: UUID) -> Model: ...
