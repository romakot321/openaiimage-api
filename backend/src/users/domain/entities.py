from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    external_id: str
    app_bundle: str
    tokens: int


class UserCreate(BaseModel):
    external_id: str
    app_bundle: str
    tokens: int = 0


class UserUpdate(BaseModel):
    tokens: int | None = None
