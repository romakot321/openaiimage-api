from uuid import UUID
from openai import BaseModel
from pydantic import ConfigDict


class ContextCreateDTO(BaseModel):
    user_id: str


class ContextTaskDTO(BaseModel):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ContextReadDTO(BaseModel):
    id: UUID
    user_id: str
    tasks: list[ContextTaskDTO]
    text_available: int
    images_available: int


class ContextUsageDTO(BaseModel):
    id: UUID
    text_used: int
    images_used: int
