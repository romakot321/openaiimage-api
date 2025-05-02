from uuid import UUID
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field

from app.schemas import BaseSearchSchema
from app.schemas.external import ExternalImageSize, ExternalImageQuality


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


class TaskUserInputSchema(BaseModel):
    key: str
    value: str


class TaskCreateSchema(BaseModel):
    user_prompt: str | None = Field(default=None, max_length=32000)
    user_inputs: list[TaskUserInputSchema] | None = None
    model_id: str | None = None
    webhook_url: str | None = None
    size: ExternalImageSize
    quality: ExternalImageQuality
    user_id: str
    app_bundle: str

    @classmethod
    def as_form(
        cls,
        user_prompt: str | None = Form(None),
        webhook_url: str | None = Form(None),
        user_inputs: list[TaskUserInputSchema] | None = Form(None),
        model_id: str | None = Form(None),
        quality: ExternalImageQuality = Form(ExternalImageQuality.auto),
        size: ExternalImageSize = Form(),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        return cls(
            user_prompt=user_prompt,
            user_inputs=user_inputs,
            webhook_url=webhook_url,
            model_id=model_id,
            size=size,
            quality=quality,
            user_id=user_id,
            app_bundle=app_bundle,
        )
