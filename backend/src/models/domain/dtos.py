from uuid import UUID
from openai import BaseModel


class ModelListParamsDTO(BaseModel):
    page: int = 0
    count: int = 0


class ModelUserInputDTO(BaseModel):
    key: str
    description: str


class ModelReadDTO(BaseModel):
    id: UUID
    title: str
    user_inputs: list[ModelUserInputDTO]

