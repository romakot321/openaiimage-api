from uuid import UUID
import json
from fastapi import Form, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic import ValidationError
from pydantic.json_schema import SkipJsonSchema
from pydantic_core import PydanticCustomError
from fastapi.encoders import jsonable_encoder

from app.schemas import BaseSearchSchema
from app.schemas.context import ContextBuilded
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


class _TaskCreateSchema(BaseModel):
    task_type: SkipJsonSchema[str]
    context_id: UUID | str | None = None
    context: SkipJsonSchema[ContextBuilded | None] = None
    webhook_url: str | None = None
    user_id: str
    app_bundle: str

    @field_validator("context_id", mode="before")
    def validate_context_id(cls, value: str) -> UUID | str | None:
        if value is None:
            return value
        elif value == "last":
            return value

        try:
            UUID(value)
        except ValueError:
            raise PydanticCustomError(
                "Invalid context_id", "Context id should be UUID or 'last'"
            )

        return UUID(value)


class TaskTextCreateSchema(_TaskCreateSchema):
    task_type: SkipJsonSchema[str] = "text"
    prompt: str

    @classmethod
    def as_form(
        cls,
        prompt: str = Form(),
        context_id: UUID | str | None = Form(None),
        webhook_url: str | None = Form(None),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        return cls(
            prompt=prompt,
            context_id=context_id,
            user_id=user_id,
            app_bundle=app_bundle,
            webhook_url=webhook_url
        )


class TaskImageCreateSchema(_TaskCreateSchema):
    task_type: SkipJsonSchema[str] = "image"
    user_prompt: str | None = Field(default=None, max_length=32000)
    user_inputs: list[TaskUserInputSchema] | None = None
    model_id: str | None = None
    size: ExternalImageSize
    quality: ExternalImageQuality

    @classmethod
    def as_form(
        cls,
        user_prompt: str | None = Form(None),
        webhook_url: str | None = Form(None),
        context_id: UUID | str | None = Form(None),
        user_inputs: list[str] | None = Form(None),
        model_id: str | None = Form(None),
        quality: ExternalImageQuality = Form(ExternalImageQuality.auto),
        size: ExternalImageSize = Form(),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        user_inputs_validated = []
        try:
            for inp in user_inputs:
                if isinstance(inp, str):
                    inp = json.loads(inp)
                if not isinstance(inp, list):
                    inp = [inp]
                for i in inp:
                    user_inputs_validated.append(TaskUserInputSchema.model_validate(i))
        except ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=422,
            )
        return cls(
            user_prompt=user_prompt,
            user_inputs=user_inputs_validated,
            context_id=context_id,
            webhook_url=webhook_url,
            model_id=model_id,
            size=size,
            quality=quality,
            user_id=user_id,
            app_bundle=app_bundle,
        )


class TaskStatisticsSchema(BaseModel):
    remaining_tokens: int
    remaining_requests: int
