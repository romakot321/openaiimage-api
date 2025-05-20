import io
from uuid import UUID
from openai import BaseModel
from pydantic import ConfigDict


class ModelUserInput(BaseModel):
    key: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class Model(BaseModel):
    id: UUID
    text: str
    title: str
    user_inputs: list[ModelUserInput]
    image: io.BytesIO | None = None
    category_name: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class ModelCategory(BaseModel):
    id: UUID
    name: str
    models: list[Model]


class ModelList(BaseModel):
    page: int
    count: int
