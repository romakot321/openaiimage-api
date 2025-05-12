from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.db.tables import ContextEntityRole


class ContextEntitySchema(BaseModel):
    content: str
    role: ContextEntityRole
    context_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ContextSchema(BaseModel):
    id: UUID
    user_id: str
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
