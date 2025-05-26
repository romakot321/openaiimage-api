from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ModelListParamsDTO(BaseModel):
    page: int = 0
    count: int = 0
    enabled: bool | None = None


class ModelUserInputDTO(BaseModel):
    key: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ModelReadDTO(BaseModel):
    id: UUID
    title: str
    user_inputs: list[ModelUserInputDTO]

    model_config = ConfigDict(from_attributes=True)


class ModelCategoryReadDTO(BaseModel):
    id: UUID
    name: str
    models: list[ModelReadDTO]

