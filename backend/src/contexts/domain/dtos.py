from uuid import UUID
from openai import BaseModel


class ContextCreateDTO(BaseModel):
    user_id: str


class ContextReadDTO(BaseModel):
    id: UUID
    user_id: str
    text_available: int
    images_available: int


class ContextUsageDTO(BaseModel):
    text_used: int
    images_used: int
