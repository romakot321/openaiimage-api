import asyncio
from uuid import UUID
import io
import base64

import redis
import rq

from rq.job import Dependency
from src.contexts.presentation.dependencies import get_context_task_adapter
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPTInput,
)
from src.integration.infrastructure.external_api.openai.schemas.responses import (
    OpenAIResponse,
)
from src.models.domain.interfaces.model_uow import IModelUnitOfWork
from src.tasks.application.use_cases.task_run import (
    _run_task_image2image_openai,
    _run_task_text2image_openai,
    _run_task_text2text_openai,
)
from src.tasks.presentation.dependencies import get_task_uow, get_task_webhook_client
from src.core.rq import task_queue
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.factories import (
    OpenAIGPTInputFromOpenAIResponseFactory,
    OpenAIRequestFromDTOFactory,
)
from src.tasks.domain.interfaces.task_context_source import (
    ITaskContextSource,
)
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
)
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def send_task_webhook(task_id: UUID, webhook_url: str):
    async with get_task_uow() as uow:
        task = await uow.tasks.get_by_pk(task_id)
    webhook_client = get_task_webhook_client()
    await webhook_client.send_webhook(task, webhook_url)


async def enqueue_image2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    images: list[io.BytesIO],
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
    model_uow: IModelUnitOfWork,
):
    context, model = None, None
    if schema.context_id:
        context = await context_client.get_task_context(
            schema.context_id, schema.user_id
        )
    if schema.model_id is not None:
        async with model_uow:
            model = await model_uow.models.get_by_pk(schema.model_id)
    request = OpenAIRequestFromDTOFactory().make_gpt_image_1_request(
        schema, images, context, model
    )
    job_id = task_queue.enqueue(
        _run_task_image2image_openai,
        task_id,
        request.model_dump(mode="json", context={"encode_image": True}),
    )
    if schema.webhook_url:
        dependency = Dependency(jobs=[job_id], allow_failure=True)
        task_queue.enqueue(
            send_task_webhook, task_id, schema.webhook_url, depends_on=dependency
        )


async def enqueue_text2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
    model_uow: IModelUnitOfWork,
):
    context, model = None, None
    if schema.context_id:
        context = await context_client.get_task_context(
            schema.context_id, schema.user_id
        )
    if schema.model_id is not None:
        async with model_uow:
            model = await model_uow.models.get_by_pk(schema.model_id)
    request = OpenAIRequestFromDTOFactory().make_gpt_image_1_request(
        schema, context=context, model=model
    )
    job_id = task_queue.enqueue(
        _run_task_text2image_openai,
        task_id,
        request.model_dump(mode="json", context={"encode_image": True}),
    )
    if schema.webhook_url:
        dependency = Dependency(jobs=[job_id], allow_failure=True)
        task_queue.enqueue(
            send_task_webhook, task_id, schema.webhook_url, depends_on=dependency
        )


async def enqueue_text2text_task(
    task_id: UUID,
    schema: TaskCreateTextDTO,
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
):
    context = None
    if schema.context_id:
        context = await context_client.get_task_context(
            schema.context_id, schema.user_id
        )
    request = OpenAIRequestFromDTOFactory().make_gpt_4_request(schema, context)
    job_id = task_queue.enqueue(
        _run_task_text2text_openai,
        task_id,
        request.model_dump(mode="json"),
    )
    if schema.webhook_url:
        dependency = Dependency(jobs=[job_id], allow_failure=True)
        task_queue.enqueue(
            send_task_webhook, task_id, schema.webhook_url, depends_on=dependency
        )
