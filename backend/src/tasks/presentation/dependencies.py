from typing import Annotated

from fastapi import Depends, HTTPException, status
from src.auth.presentation.dependencies import CurrentUserDepend
from src.contexts.presentation.dependencies import get_context_task_adapter
from src.integration.presentation.dependencies import get_openai_adapter
from src.tasks.domain.interfaces.task_context_source import ITaskContextSource
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from src.tasks.domain.interfaces.task_statistics_unit_of_work import ITaskStatisticsUnitOfWork
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.infrastructure.db.unit_of_work import PGTaskUnitOfWork
from src.tasks.infrastructure.http.http_client import AiohttpClient
from src.tasks.infrastructure.http.task_webhook_client import TaskWebhookClient
from src.tasks.infrastructure.redis.statistics_unit_of_work import RedisTaskStatisticsUnitOfWork
from src.users.domain.entities import User


def get_task_statistics_uow() -> ITaskStatisticsUnitOfWork:
    return RedisTaskStatisticsUnitOfWork()


def get_task_uow() -> ITaskUnitOfWork:
    return PGTaskUnitOfWork()


def get_task_webhook_client() -> TaskWebhookClient:
    return TaskWebhookClient(client=AiohttpClient())


def validate_tokens_balance(user: CurrentUserDepend) -> User:
    if user.tokens <= 0:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient tokens balance")
    return user


ValidateTokensBalanceDepend = Annotated[User, Depends(validate_tokens_balance)]
TaskUoWDepend = Annotated[ITaskUnitOfWork, Depends(get_task_uow)]
OpenAIAdapterDepend = Annotated[ITaskSourceClient, Depends(get_openai_adapter)]
TaskContextAdapterDepend = Annotated[ITaskContextSource, Depends(get_context_task_adapter)]
TaskStatisticsUoWDepend = Annotated[ITaskStatisticsUnitOfWork, Depends(get_task_statistics_uow)]
