from uuid import UUID

from backend.src.contexts.domain.interfaces.context_uow import IContextUnitOfWork


async def delete_context(context_id: UUID, uow: IContextUnitOfWork):
    async with uow:
        await uow.contexts.delete_by_pk(context_id)
        await uow.commit()
