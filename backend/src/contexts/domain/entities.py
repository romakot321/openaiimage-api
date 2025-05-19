from enum import Enum
from uuid import UUID
from openai import BaseModel
from pydantic import ConfigDict


class ContextEntityContentType(str, Enum):
    image = 'image'
    text = 'text'


class ContextEntityRole(str, Enum):
    user = 'user'
    assistant = 'assistant'
    system = 'system'


class ContextEntity(BaseModel):
    content_type: ContextEntityContentType
    content: str
    role: ContextEntityRole
    context_id: UUID


class ContextTask(BaseModel):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class Context(BaseModel):
    id: UUID
    user_id: str
    entities: list[ContextEntity]
    tasks: list[ContextTask]


class ContextCreate(BaseModel):
    user_id: str


class ContextEntityCreate(BaseModel):
    context_id: UUID
    content_type: ContextEntityContentType
    content: str
    role: ContextEntityRole
