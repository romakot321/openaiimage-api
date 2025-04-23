from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.schemas import BaseSearchSchema


class TaskSchema(BaseModel):
    class TaskItem(BaseModel):
        id: int

        model_config = ConfigDict(from_attributes=True)

    id: UUID
    items: list[TaskItem]

    model_config = ConfigDict(from_attributes=True)


class TaskShortSchema(BaseModel):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class TaskUpdateSchema(BaseModel):
    pass


class TaskSearchSchema(BaseSearchSchema):
    pass


class TaskCreateSchema(BaseModel):
    text: str
