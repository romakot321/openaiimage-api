import io
from uuid import UUID
from openai import BaseModel
from pydantic import ConfigDict


class Model(BaseModel):
    id: UUID
    text: str
    title: str
    image: io.BytesIO | None = None
    category_name: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ModelUserInput(BaseModel):
    model_id: UUID
    key: str
    description: str


class ModelCategory(BaseModel):
    id: UUID
    name: str


class ModelList(BaseModel):
    page: int
    count: int
