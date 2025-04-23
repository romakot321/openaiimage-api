from uuid import UUID
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

    model_config = ConfigDict(from_attributes=True)


class TaskCreateSchema(BaseModel):
    prompt: str | None = None
    model_id: str | None = None
    size: ExternalImageSize
    user_id: str
    app_bundle: str

    @classmethod
    def as_form(
        cls,
        prompt: str | None = Form(None),
        model_id: str | None = Form(None),
        size: ExternalImageSize = Form(),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        return cls(
            prompt=prompt,
            model_id=model_id,
            size=size,
            user_id=user_id,
            app_bundle=app_bundle,
        )
