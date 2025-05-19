import base64
from uuid import UUID
import io


from src.core.filesystem_storage import storage
from src.core.config import settings
from src.integration.infrastructure.external_api.openai.schemas.requests import OpenAIGPT4Request, OpenAIGPTImage1Request
from src.integration.infrastructure.external_api.openai.schemas.responses import OpenAIResponse
from src.integration.presentation.dependencies import get_openai_adapter
from src.tasks.domain.entities import TaskItemCreate
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
    TRequestForText,
    TRequestForImage,
    TResponse,
)
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.presentation.dependencies import get_task_uow

import asyncio
from typing import Coroutine
from uuid import UUID
import io

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




def _save_result(task_id: UUID, image_encoded: str) -> str:
    filename = storage.generate_new_filename(str(task_id))
    storage.write(io.BytesIO(base64.b64decode(image_encoded.encode())), filename)
    return f"https://{settings.DOMAIN}/api/task/{filename}/result"


async def run_task_image2image(
    task_id: UUID,
    request: TRequestForImage,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
) -> TResponse:
    result = await client.generate_image2image(request)
    result.content = _save_result(task_id, result.content)
    async with uow:
        await uow.task_items.create(
            TaskItemCreate(task_id=task_id, result_url=result.content)
        )
        await uow.commit()
    return result


async def run_task_text2image(
    task_id: UUID,
    request: TRequestForImage,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
) -> TResponse:
    result = await client.generate_text2image(request)
    result.content = _save_result(task_id, result.content)
    async with uow:
        await uow.task_items.create(
            TaskItemCreate(task_id=task_id, result_url=result.content)
        )
        await uow.commit()
    return result


async def run_task_text2text(
    task_id: UUID,
    request: TRequestForText,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
) -> TResponse:
    result = await client.generate_text2text(request)
    async with uow:
        await uow.task_items.create(
            TaskItemCreate(task_id=task_id, result_url=result.content)
        )
        await uow.commit()
    return result


async def _on_task_finished_append_context(
    context_id: UUID | str, user_id: str, context_message: OpenAIGPTInput
):
    context_adapter_getter = get_context_task_adapter()
    context_adapter = await anext(context_adapter_getter)
    await context_adapter.append_task_context(context_id, context_message, user_id)
    try:
        await anext(context_adapter_getter)
    except StopAsyncIteration:
        pass


async def _on_image_task_finished(task_id, result):
    async with get_task_uow() as uow:
        task = await uow.tasks.get_by_pk(task_id)
    if task.context_id:
        context_message = (
            OpenAIGPTInputFromOpenAIResponseFactory().make_image_gpt_input(result)
        )
        await _on_task_finished_append_context(
            task.context_id, task.user_id, context_message
        )


async def _on_text_task_finished(task_id, result):
    async with get_task_uow() as uow:
        task = await uow.tasks.get_by_pk(task_id)
    print("TEXT TASK", task, task_id, task.context_id)
    if task.context_id:
        context_message = (
            OpenAIGPTInputFromOpenAIResponseFactory().make_text_gpt_input(result)
        )
        print(context_message)
        await _on_task_finished_append_context(
            task.context_id, task.user_id, context_message
        )


async def _run_task_text2text_openai(task_id: UUID, request: OpenAIGPT4Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    result = await run_task_text2text(task_id, request, client, uow)
    await _on_text_task_finished(task_id, result)
    return result


async def _run_task_text2image_openai(task_id: UUID, request: OpenAIGPTImage1Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    result = await run_task_text2image(task_id, request, client, uow)
    await _on_image_task_finished(task_id, result)
    return result


async def _run_task_image2image_openai(task_id: UUID, request: OpenAIGPTImage1Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    result = await run_task_image2image(task_id, request, client, uow)
    await _on_image_task_finished(task_id, result)
    return result
