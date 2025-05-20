from typing import Literal
from uuid import UUID
import json
from fastapi import Form
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

from src.tasks.domain.entities import TaskResultQuality, TaskResultSize


class TaskUserInputDTO(BaseModel):
    key: str
    value: str


class TaskCreateTextDTO(BaseModel):
    prompt: str
    user_id: str
    app_bundle: str
    context_id: UUID | Literal['last'] | None = None
    webhook_url: str | None = None


class TaskCreateImageDTO(BaseModel):
    user_id: str
    app_bundle: str
    size: TaskResultSize
    quality: TaskResultQuality = TaskResultQuality.auto
    user_inputs: list[TaskUserInputDTO] | None = None
    user_prompt: str | None = None
    model_id: UUID | None = None
    context_id: UUID | Literal['last'] | None = None
    webhook_url: str | None = None

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

    @classmethod
    def as_form(
        cls,
        user_prompt: str | None = Form(None),
        webhook_url: str | None = Form(None),
        context_id: UUID | Literal['last'] | None = Form(None),
        user_inputs: list[str] | None = Form(None),
        model_id: UUID | None = Form(None),
        quality: TaskResultQuality = Form(TaskResultQuality.auto),
        size: TaskResultSize = Form(),
        user_id: str = Form(),
        app_bundle: str = Form(),
    ):
        user_inputs_validated = []
        for inp in (user_inputs or []):
            if isinstance(inp, str):
                inp = json.loads(inp)
            if not isinstance(inp, list):
                inp = [inp]
            for i in inp:
                user_inputs_validated.append(TaskUserInputDTO.model_validate(i))
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



class TaskItemDTO(BaseModel):
    result_url: str


class TaskReadDTO(BaseModel):
    id: UUID
    error: str | None = None
    items: list[TaskItemDTO]


class TaskStatisticsDTO(BaseModel):
    remaining_tokens: int
    remaining_requests: int
