from uuid import UUID
import io

from src.core.rq import task_queue
from backend.src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from backend.src.tasks.domain.entities import TaskItemCreate, TaskUpdate
from backend.src.tasks.domain.factories import OpenAIRequestFactory
from backend.src.tasks.domain.interfaces.task_context_source import (
    ITaskContextSource,
    TContextMessage,
)
from backend.src.tasks.domain.interfaces.task_source_client import (
    ITaskSourceClient,
    TRequestForText,
    TRequestForImage,
    TResponse,
)
from backend.src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def run_task_image2image(
    task_id: UUID,
    request: TRequestForImage,
    client: ITaskSourceClient,
    uow: ITaskUnitOfWork,
) -> TResponse:
    result = await client.generate_image2image(request)
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


async def enqueue_image2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    images: list[io.BytesIO],
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
):
    context = None
    if schema.context_id:
        context = await context_client.get_task_context(schema.context_id)
    request = OpenAIRequestFactory().make_gpt_image_1_request(schema, images, context)
    task_queue.enqueue(run_task_image2image, task_id, request, client, uow)


async def enqueue_text2image_task(
    task_id: UUID,
    schema: TaskCreateImageDTO,
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
):
    context = None
    if schema.context_id:
        context = await context_client.get_task_context(schema.context_id)
    request = OpenAIRequestFactory().make_gpt_image_1_request(schema, context=context)
    task_queue.enqueue(run_task_text2image, task_id, request, client, uow)


async def enqueue_text2text_task(
    task_id: UUID,
    schema: TaskCreateTextDTO,
    client: ITaskSourceClient,
    context_client: ITaskContextSource,
    uow: ITaskUnitOfWork,
):
    context = None
    if schema.context_id:
        context = await context_client.get_task_context(schema.context_id)
    request = OpenAIRequestFactory().make_gpt_4_request(schema, context)
    task_queue.enqueue(run_task_text2text, task_id, request, client, uow)
