from typing import Annotated

from fastapi import Depends
from src.contexts.presentation.dependencies import get_context_task_adapter
from src.integration.presentation.dependencies import get_openai_adapter
from src.tasks.domain.interfaces.task_context_source import ITaskContextSource
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
OpenAIAdapterDepend = Annotated[ITaskSourceClient, Depends(get_openai_adapter)]
TaskContextAdapterDepend = Annotated[ITaskContextSource, Depends(get_context_task_adapter)]
