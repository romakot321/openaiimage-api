from uuid import UUID
from pydantic import BaseModel, ConfigDict, AliasChoices, Field

from app.schemas.model import ModelSchema


class ModelCategorySchema(BaseModel):
    id: UUID
    name: str
    models: list[ModelSchema] = Field(validation_alias=AliasChoices('models', 'prompts'))

    model_config = ConfigDict(from_attributes=True)


class ModelCategorySearchSchema(BaseModel):
    page: int = 0
    count: int = 10

