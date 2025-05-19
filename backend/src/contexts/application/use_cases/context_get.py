from uuid import UUID

from src.core.config import settings
from src.contexts.domain.dtos import ContextReadDTO
from src.contexts.domain.interfaces.context_uow import IContextUnitOfWork


async def get_context(context_id: UUID, uow: IContextUnitOfWork) -> ContextReadDTO:
    async with uow:
        context = await uow.contexts.get_by_pk(context_id)
        usage = await uow.context_entity.get_context_usage(context_id)
    return ContextReadDTO(
        id=context_id,
        user_id=context.user_id,
        tasks=context.tasks,
        text_available=settings.CONTEXT_MAX_SYMBOLS - usage.text_used,
        images_available=settings.CONTEXT_MAX_IMAGES - usage.images_used
    )
