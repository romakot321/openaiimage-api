from uuid import UUID
from enum import Enum
from fastapi import Form
from pydantic import BaseModel, ConfigDict

from app.schemas import BaseSearchSchema
from app.schemas.external import ExternalImageSize


class TaskSchema(BaseModel):
    class TaskItem(BaseModel):
        id: int
        result_url: str

        model_config = ConfigDict(from_attributes=True)

    id: UUID
    error: str | None = None
    items: list[TaskItem]

    model_config = ConfigDict(from_attributes=True)


class TaskShortSchema(BaseModel):
    id: UUID
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ImageSize(Enum):
    square_hd = "square_hd"
    square = "square"
    portrait_4_3 = "portrait_4_3"
    portrait_16_9 = "portrait_16_9"
    landscape_4_3 = "landscape_4_3"
    landscape_16_9 = "landscape_16_9"


class TaskCreateSchema(BaseModel):
    user_prompt: str | None = None
    model_id: str | None = None
    size: ImageSize
    user_id: str
    app_bundle: str

    @classmethod
    def as_form(
        cls,
        user_prompt: str | None = Form(None),
        model_id: str | None = Form(None),
        size: ExternalImageSize = Form(),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        return cls(
            user_prompt=user_prompt,
            model_id=model_id,
            size=size,
            user_id=user_id,
            app_bundle=app_bundle,
        )
