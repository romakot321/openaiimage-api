import base64
import logging
from typing import Any, Coroutine
from uuid import UUID
import io
import binascii


from fastapi import HTTPException
from src.core.filesystem_storage import storage
from src.core.config import settings
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPT4Request,
    OpenAIGPTImage1Request,
)
from src.integration.infrastructure.external_api.openai.schemas.responses import (
    OpenAIResponse,
)
from src.integration.presentation.dependencies import get_openai_adapter
from src.tasks.domain.entities import (
    TaskItemCreate,
    TaskStatisticsRemaining,
    TaskUpdate,
)
from src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
    TRequestForText,
    TRequestForImage,
    TResponse,
)
from src.tasks.domain.interfaces.task_statistics_unit_of_work import (
    ITaskStatisticsUnitOfWork,
)
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.domain.interfaces.tokens_uow import ITokensUnitOfWork
from src.tasks.presentation.dependencies import get_task_statistics_uow, get_task_uow

from src.contexts.presentation.dependencies import get_context_task_adapter
from src.integration.infrastructure.external_api.openai.schemas.requests import (
    OpenAIGPTInput,
)
from src.tasks.domain.factories import (
    OpenAIGPTInputFromOpenAIRequestFactory,
    OpenAIGPTInputFromOpenAIResponseFactory,
)
from src.users.presentation.dependencies import get_tokens_uow

logger = logging.getLogger(__name__)


def _save_response(task_id: UUID, image_encoded: str) -> str:
    try:
        image_decoded = io.BytesIO(base64.b64decode(image_encoded.encode()))
    except binascii.Error:  # If input not image, return input
        return image_encoded
    filename = storage.generate_new_filename(str(task_id))
    storage.write(image_decoded, filename)
    return f"https://{settings.DOMAIN}/api/task/{filename}/result"


async def _run_task(
    coroutine: Coroutine[Any, Any, TResponse],
    task_id: UUID,
    uow: ITaskUnitOfWork,
    client: ITaskSourceClient,
    statistics_uow: ITaskStatisticsUnitOfWork,
) -> TResponse:
    try:
        result = await coroutine
    except Exception as e:
        async with uow:
            await uow.tasks.update(task_id, TaskUpdate(error=str(e)))
            await uow.commit()
        raise e

    result.content = _save_response(task_id, result.content)
    async with uow:
        await uow.task_items.create(
            TaskItemCreate(
                task_id=task_id,
                result_url=result.content,
                used_tokens=result.used_tokens or 0,
            )
        )
        await uow.commit()

    if result.remaining_requests is not None and result.remaining_tokens is not None:
        async with statistics_uow:
            try:
                await statistics_uow.statistics.store_remaining(
                    TaskStatisticsRemaining(**result.model_dump())
                )
            except Exception as e:
                logger.exception(e)

    return result


async def write_off_user_tokens(
    task_id: UUID, tokens_uow: ITokensUnitOfWork, uow: ITaskUnitOfWork
):
    async with uow:
        task = await uow.tasks.get_by_pk(task_id)
    async with tokens_uow:
        try:
            await tokens_uow.write_off_tokens(
                task.user_id, task.app_bundle, settings.GENERATION_TOKENS_COST
            )
        except HTTPException as e:
            if e.status_code in (404, 409):
                return
            raise e
        await tokens_uow.commit()


async def run_task_image2image(
    task_id: UUID,
    request: TRequestForImage,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
    statistics_uow: ITaskStatisticsUnitOfWork,
    tokens_uow: ITokensUnitOfWork,
) -> TResponse:
    method = client.generate_image2image(request)
    result = await _run_task(method, task_id, uow, client, statistics_uow)
    await write_off_user_tokens(task_id, tokens_uow, uow)
    return result


async def run_task_text2image(
    task_id: UUID,
    request: TRequestForImage,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
    statistics_uow: ITaskStatisticsUnitOfWork,
    tokens_uow: ITokensUnitOfWork,
) -> TResponse:
    method = client.generate_text2image(request)
    result = await _run_task(method, task_id, uow, client, statistics_uow)
    await write_off_user_tokens(task_id, tokens_uow, uow)
    return result


async def run_task_text2text(
    task_id: UUID,
    request: TRequestForText,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
    statistics_uow: ITaskStatisticsUnitOfWork,
    tokens_uow: ITokensUnitOfWork,
) -> TResponse:
    method = client.generate_text2text(request)
    result = await _run_task(method, task_id, uow, client, statistics_uow)
    await write_off_user_tokens(task_id, tokens_uow, uow)
    return result


async def _on_task_finished_append_context(
    context_id: UUID | str, user_id: str, context_messages: list[OpenAIGPTInput]
):
    context_adapter_getter = get_context_task_adapter()
    context_adapter = await anext(context_adapter_getter)
    await context_adapter.append_task_context(context_id, context_messages, user_id)
    try:
        await anext(context_adapter_getter)
    except StopAsyncIteration:
        pass


async def _on_image_task_finished(task_id, request, result, uow):
    task = await uow.tasks.get_by_pk(task_id)
    if not task.context_id:
        return

    context_messages = []
    if isinstance(request, OpenAIGPTImage1Request):
        context_messages.append(
            OpenAIGPTInputFromOpenAIRequestFactory().make_image_gpt_input(request)
        )
    else:
        raise TypeError(
            f"Failed to append context: Unknown request type: {type(request)}"
        )

    context_messages.append(
        OpenAIGPTInputFromOpenAIResponseFactory().make_image_gpt_input(result)
    )
    await _on_task_finished_append_context(
        task.context_id, task.user_id, context_messages
    )


async def _on_text_task_finished(task_id, request, result, uow):
    task = await uow.tasks.get_by_pk(task_id)
    if not task.context_id:
        return

    context_messages = []
    if isinstance(request, OpenAIGPT4Request):
        context_messages.append(
            OpenAIGPTInputFromOpenAIRequestFactory().make_text_gpt_input(request)
        )
    else:
        raise TypeError(
            f"Failed to append context: Unknown request type: {type(request)}"
        )

    context_messages.append(
        OpenAIGPTInputFromOpenAIResponseFactory().make_text_gpt_input(result)
    )
    await _on_task_finished_append_context(
        task.context_id, task.user_id, context_messages
    )


async def _run_task_text2text_openai(
    task_id: UUID, request_raw: dict
) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    statistics_uow = get_task_statistics_uow()
    tokens_uow = get_tokens_uow()
    async with get_task_uow() as uow:
        request = OpenAIGPT4Request.model_validate(request_raw)
        result = await run_task_text2text(task_id, request, client, uow, statistics_uow, tokens_uow)
        await _on_text_task_finished(task_id, request, result, uow)
    return result


async def _run_task_text2image_openai(
    task_id: UUID, request_raw: dict
) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    statistics_uow = get_task_statistics_uow()
    tokens_uow = get_tokens_uow()
    async with get_task_uow() as uow:
        request = OpenAIGPTImage1Request.model_validate(request_raw)
        result = await run_task_text2image(
            task_id, request, client, uow, statistics_uow, tokens_uow
        )
        await _on_image_task_finished(task_id, request, result, uow)
    return result


async def _run_task_image2image_openai(
    task_id: UUID, request_raw: dict
) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    statistics_uow = get_task_statistics_uow()
    tokens_uow = get_tokens_uow()
    async with get_task_uow() as uow:
        request = OpenAIGPTImage1Request.model_validate(request_raw)
        result = await run_task_image2image(
            task_id, request, client, uow, statistics_uow, tokens_uow
        )
        await _on_image_task_finished(task_id, request, result, uow)
    return result
