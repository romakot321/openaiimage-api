from typing import Annotated, AsyncGenerator

from fastapi import Depends
from src.contexts.domain.interfaces.context_uow import IContextUnitOfWork
from src.contexts.infrastructure.db.adapter import ContextTaskAdapter
from src.contexts.infrastructure.db.unit_of_work import PGContextUnitOfWork
from src.tasks.domain.interfaces.task_context_source import ITaskContextSource


def get_context_uow() -> IContextUnitOfWork:
    return PGContextUnitOfWork()


async def get_context_task_adapter() -> AsyncGenerator[ITaskContextSource]:
    async with PGContextUnitOfWork() as context_uow:
        yield ContextTaskAdapter(context_uow)


ContextUoWDepend = Annotated[IContextUnitOfWork, Depends(get_context_uow)]
ContextTaskAdapterDepend = Annotated[ITaskContextSource, Depends(get_context_task_adapter)]
