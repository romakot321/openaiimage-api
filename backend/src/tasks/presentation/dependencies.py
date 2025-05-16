from typing import Annotated

from fastapi import Depends
from backend.src.contexts.presentation.dependencies import get_context_task_adapter
from backend.src.integration.presentation.dependencies import get_openai_adapter
from backend.src.tasks.domain.interfaces.task_context_source import ITaskContextSource
from backend.src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from backend.src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from backend.src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
OpenAIAdapterDepend = Annotated[ITaskSourceClient, Depends(get_openai_adapter)]
TaskContextAdapterDepend = Annotated[ITaskContextSource, Depends(get_context_task_adapter)]
