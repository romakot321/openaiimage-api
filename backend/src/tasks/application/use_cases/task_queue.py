import asyncio
from typing import Coroutine
from uuid import UUID
import io

import redis
import rq

from src.contexts.presentation.dependencies import get_context_task_adapter
from src.integration.infrastructure.external_api.openai.schemas.requests import OpenAIGPTInput
from src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from src.models.domain.interfaces.model_uow import IModelUnitOfWork
from src.tasks.application.use_cases.task_run import (
    _run_task_image2image_openai,
    _run_task_text2image_openai,
    _run_task_text2text_openai
)
from src.tasks.presentation.dependencies import get_task_uow
from src.core.rq import task_queue
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.factories import OpenAIGPTInputFromOpenAIResponseFactory, OpenAIRequestFromDTOFactory
from src.tasks.domain.interfaces.task_context_source import (
    ITaskContextSource,
)
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
)
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def _on_task_finished_append_context(context_id: UUID | str, user_id: str, context_message: OpenAIGPTInput):
    context_adapter_getter = get_context_task_adapter()
    context_adapter = await anext(context_adapter_getter)
    await context_adapter.append_task_context(context_id, context_message, user_id)
    try:
        await anext(context_adapter_getter)
    except StopAsyncIteration:
        pass


def on_image_task_finished(
    job: rq.job.Job, connection: redis.Redis, result: OpenAIResponse, *args, **kwargs
):
    async def _async_task(job: rq.job.Job, connection: redis.Redis, result: OpenAIResponse, *args, **kwargs):
        task_id: UUID = job.args[0]
        async with get_task_uow() as uow:
            task = await uow.tasks.get_by_pk(task_id)
        if task.context_id:
            context_message = OpenAIGPTInputFromOpenAIResponseFactory().make_image_gpt_input(result)
            await _on_task_finished_append_context(task.context_id, task.user_id, context_message)

    loop = asyncio.get_event_loop()
    loop.create_task(_async_task(job, connection, result, *args, **kwargs))


def on_text_task_finished(
    job: rq.job.Job, connection: redis.Redis, result: OpenAIResponse, *args, **kwargs
):
    async def _async_task(job, connection, result, *args, **kwargs):
        task_id: UUID = job.args[0]
        async with get_task_uow() as uow:
            task = await uow.tasks.get_by_pk(task_id)
        if task.context_id:
            context_message = OpenAIGPTInputFromOpenAIResponseFactory().make_text_gpt_input(result)
            await _on_task_finished_append_context(task.context_id, task.user_id, context_message)

    loop = asyncio.get_event_loop()
    loop.create_task(_async_task(job, connection, result, *args, **kwargs))


async def enqueue_image2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    images: list[io.BytesIO],
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
    model_uow: IModelUnitOfWork
):
    context, model = None, None
    if schema.context_id:
        context = await context_client.get_task_context(
            schema.context_id, schema.user_id
        )
    if schema.model_id is not None:
        async with model_uow:
            model = await model_uow.models.get_by_pk(schema.model_id)
    request = OpenAIRequestFromDTOFactory().make_gpt_image_1_request(schema, images, context, model)
    task_queue.enqueue(_run_task_image2image_openai, task_id, request, on_success=rq.Callback(on_image_task_finished))


async def enqueue_text2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
    model_uow: IModelUnitOfWork
):
    context, model = None, None
    if schema.context_id:
        context = await context_client.get_task_context(
            schema.context_id, schema.user_id
        )
    if schema.model_id is not None:
        async with model_uow:
            model = await model_uow.models.get_by_pk(schema.model_id)
    request = OpenAIRequestFromDTOFactory().make_gpt_image_1_request(schema, context=context, model=model)
    task_queue.enqueue(_run_task_text2image_openai, task_id, request, on_success=rq.Callback(on_image_task_finished))


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
    task_queue.enqueue(_run_task_text2text_openai, task_id, request, on_success=rq.Callback(on_text_task_finished))
