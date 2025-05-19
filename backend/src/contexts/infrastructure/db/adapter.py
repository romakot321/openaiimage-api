from uuid import UUID
import logging

from fastapi import HTTPException
from src.contexts.domain.entities import (
    Context,
    ContextEntityContentType,
    ContextEntityCreate,
)
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

logger = logging.getLogger(__name__)


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
        self, context_id: UUID | str, user_id: str | None = None
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
        if isinstance(context_id, str):
            context_id = (await self._get_context(context_id, user_id)).id
        usage = await self.context_uow.context_entity.get_context_usage(context_id)
        return {
            "context_id": context_id,
            "text_left": settings.CONTEXT_MAX_SYMBOLS - usage.text_used,
            "images_left": settings.CONTEXT_MAX_IMAGES - usage.images_used,
        }

    async def _strip_context(
        self, context_id: UUID, text_strip_amount: int, image_strip_amount: int
    ):
        entities = await self.context_uow.context_entity.get_list_by_context_id(
            context_id
        )
        text_deleted, image_deleted = 0, 0
        for entity in entities[::-1]:
            await self.context_uow.context_entity.delete_by_pk(entity.id)
            if (
                image_strip_amount > image_deleted
                and entity.content_type == ContextEntityContentType.image
            ):
                image_deleted -= 1
            elif (
                text_strip_amount > text_deleted
                and entity.content_type == ContextEntityContentType.text
            ):
                text_deleted -= len(entity.content)

            if (
                text_strip_amount <= text_deleted
                and image_strip_amount <= image_deleted
            ):
                break
        logger.debug(f"Stripped {context_id} for {text_deleted=} {image_deleted=}")

    async def append_task_context(
        self,
        context_id: UUID | str,
        messages: list[OpenAIGPTInput],
        user_id: str | None = None,
    ) -> None:
        context_left = await self.get_task_context_left(context_id, user_id)
        if context_left["text_left"] <= 0 or context_left["images_left"] <= 0:
            await self._strip_context(
                context_left["context_id"],
                1 * int(context_left["text_left"] <= 0),
                1 * int(context_left["images_left"]),
            )
        for message in messages:
            context_entity = OpenAIGPTInputToContextEntityMapper().map_one(
                message, context_left["context_id"]
            )
            request = ContextEntityCreate(**context_entity.model_dump(exclude="id"))
            await self.context_uow.context_entity.create(request)
        await self.context_uow.commit()
