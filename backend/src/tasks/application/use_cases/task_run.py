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


async def _run_task_text2text_openai(task_id: UUID, request: OpenAIGPT4Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    return await run_task_text2text(task_id, request, client, uow)


async def _run_task_text2image_openai(task_id: UUID, request: OpenAIGPTImage1Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    return await run_task_text2image(task_id, request, client, uow)


async def _run_task_image2image_openai(task_id: UUID, request: OpenAIGPTImage1Request) -> OpenAIResponse:
    """Implemented for rq integration. Do not use it directly"""
    client = get_openai_adapter()
    uow = get_task_uow()
    return await run_task_image2image(task_id, request, client, uow)
