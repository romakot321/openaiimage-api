from backend.src.contexts.domain.dtos import ContextCreateDTO, ContextReadDTO
from backend.src.contexts.domain.entities import Context, ContextCreate
from backend.src.contexts.domain.interfaces.context_uow import IContextUnitOfWork
from src.core.config import settings


async def create_context(
    context_data: ContextCreateDTO, uow: IContextUnitOfWork
) -> ContextReadDTO:
    request = ContextCreate(**context_data.model_dump())
    async with uow:
        context = await uow.contexts.create(request)
        await uow.commit()
    return ContextReadDTO(
        **context.model_dump(),
        text_available=settings.CONTEXT_MAX_SYMBOLS,
        images_available=settings.CONTEXT_MAX_IMAGES,
    )
