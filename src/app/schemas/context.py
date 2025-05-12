from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.db.tables import ContextEntityRole


class ContextEntitySchema(BaseModel):
    content: str
    role: ContextEntityRole
    context_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ContextTaskSchema(BaseModel):
    class TaskItem(BaseModel):
        id: int
        result_url: str

        model_config = ConfigDict(from_attributes=True)

    id: UUID
    items: list[TaskItem]

    model_config = ConfigDict(from_attributes=True)


class ContextSchema(BaseModel):
    id: UUID
    user_id: str
    tasks: list[ContextTaskSchema]
    text_available: int
    images_available: int

    model_config = ConfigDict(from_attributes=True)


class ContextCreateSchema(BaseModel):
    user_id: str


class ContextBuildedEntity(BaseModel):
    role: ContextEntityRole
    content: str


class ContextBuilded(BaseModel):
    entities: list[ContextBuildedEntity]
    images_filenames: list[str]
