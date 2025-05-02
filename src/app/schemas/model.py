from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ModelUserInputSchema(BaseModel):
    key: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ModelSchema(BaseModel):
    id: UUID
    title: str
    user_inputs: list[ModelUserInputSchema]
    for_image: bool

    model_config = ConfigDict(from_attributes=True)


class ModelSearchSchema(BaseModel):
    page: int = 0
    count: int = 100

