from uuid import UUID
from backend.src.contexts.domain.entities import ContextEntityCreate
from backend.src.contexts.domain.interfaces.context_uow import IContextUnitOfWork
from src.core.filesystem_storage import storage
from src.core.config import settings
from backend.src.contexts.domain.mappers import (
    ContextEntityToOpenAIGPTInputMapper,
    OpenAIGPTInputToContextEntityMapper,
)
from backend.src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPTInput,
)
from backend.src.tasks.domain.interfaces.task_context_source import ITaskContextSource


class ContextTaskAdapter(ITaskContextSource[OpenAIGPTInput]):
    def __init__(self, context_uow: IContextUnitOfWork) -> None:
        self.context_uow = context_uow

    # TODO: Add support of context_id = 'last'

    async def get_task_context(self, context_id: UUID) -> list[OpenAIGPTInput]:
        context = await self.context_uow.contexts.get_by_pk(context_id)
        gpt_inputs = ContextEntityToOpenAIGPTInputMapper(storage).map(context.entities)
        return gpt_inputs

    async def get_task_context_left(self, context_id: UUID) -> dict:
        usage = await self.context_uow.context_entity.get_context_usage(context_id)
        return {
            "text_left": settings.CONTEXT_MAX_SYMBOLS - usage.text_used,
            "images_left": settings.CONTEXT_MAX_IMAGES - usage.images_used,
        }

    async def append_task_context(
        self, context_id: UUID, message: OpenAIGPTInput
    ) -> None:
        context_entity = OpenAIGPTInputToContextEntityMapper().map_one(
            message, context_id
        )
        request = ContextEntityCreate(**context_entity.model_dump())
        await self.context_uow.context_entity.create(request)
