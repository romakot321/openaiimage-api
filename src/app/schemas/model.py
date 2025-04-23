from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ModelSchema(BaseModel):
    id: UUID
    title: str
    for_image: bool

    model_config = ConfigDict(from_attributes=True)


class ModelSearchSchema(BaseModel):
    page: int = 0
    count: int = 100

