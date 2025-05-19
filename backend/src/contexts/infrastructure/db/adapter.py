from uuid import UUID

from fastapi import HTTPException
from src.contexts.domain.entities import Context, ContextEntityCreate
from src.contexts.domain.interfaces.context_uow import IContextUnitOfWork
from src.core.filesystem_storage import storage
from src.core.config import settings
from src.contexts.domain.mappers import (
    ContextEntityToOpenAIGPTInputMapper,
    OpenAIGPTInputToContextEntityMapper,
)
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPTInput,
)
from src.tasks.domain.interfaces.task_context_source import ITaskContextSource


class ContextTaskAdapter(ITaskContextSource[OpenAIGPTInput]):
    def __init__(self, context_uow: IContextUnitOfWork) -> None:
        self.context_uow = context_uow

    async def _get_user_last_context(self, user_id: str | None) -> Context:
        if user_id is None:
            raise HTTPException(
                422, detail="User id must be filled for context_id='last'"
            )
        return await self.context_uow.contexts.get_user_last(user_id)

    async def _get_context(
        self, context_id: UUID | str, user_id: str | None
    ) -> Context:
        if context_id == "last":
            return await self._get_user_last_context(user_id)
        elif isinstance(context_id, UUID):
            return await self.context_uow.contexts.get_by_pk(context_id)
        raise HTTPException(422, detail="Unknown context_id type")

    async def get_task_context(
        self, context_id: UUID | str, user_id: str | None = None
    ) -> list[OpenAIGPTInput]:
        context = await self._get_context(context_id, user_id)
        gpt_inputs = ContextEntityToOpenAIGPTInputMapper(storage).map(context.entities)
        return gpt_inputs

    async def get_task_context_left(
        self, context_id: UUID | str, user_id: str | None = None
    ) -> dict:
        context = await self._get_context(context_id, user_id)
        usage = await self.context_uow.context_entity.get_context_usage(context.id)
        return {
            "text_left": settings.CONTEXT_MAX_SYMBOLS - usage.text_used,
            "images_left": settings.CONTEXT_MAX_IMAGES - usage.images_used,
        }

    async def append_task_context(
        self,
        context_id: UUID | str,
        message: OpenAIGPTInput,
        user_id: str | None = None,
    ) -> None:
        context = await self._get_context(context_id, user_id)
        context_entity = OpenAIGPTInputToContextEntityMapper().map_one(
            message, context.id
        )
        request = ContextEntityCreate(**context_entity.model_dump())
        await self.context_uow.context_entity.create(request)
