from io import BytesIO
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import Response

from backend.src.tasks.application.use_cases.task_status import get_task
from src.core.rq import task_queue
from backend.src.tasks.application.use_cases.task_create import create_task
from backend.src.tasks.application.use_cases.task_run import (
    enqueue_image2image_task,
    enqueue_text2image_task,
    enqueue_text2text_task,
    run_task_image2image,
    run_task_text2image,
)
from backend.src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO, TaskReadDTO
from backend.src.tasks.domain.factories import OpenAIRequestFactory
from backend.src.tasks.presentation.dependencies import (
    OpenAIAdapterDepend,
    TaskContextAdapterDepend,
    TaskUoWDepend,
)

router = APIRouter()


@router.post("/image", response_model=TaskReadDTO)
async def create_from_image_to_image(
    uow: TaskUoWDepend,
    client: OpenAIAdapterDepend,
    context_client: TaskContextAdapterDepend,
    image: UploadFile = File(),
    schema: TaskCreateImageDTO = Depends(TaskCreateImageDTO.as_form),
):
    task = await create_task(schema, uow)
    image_buffer = BytesIO(await image.read())
    await enqueue_image2image_task(task.id, schema, [image_buffer], client, context_client, uow)
    return task


@router.post("/text")
async def create_from_text_to_image(
    uow: TaskUoWDepend,
    client: OpenAIAdapterDepend,
    context_client: TaskContextAdapterDepend,
    schema: TaskCreateImageDTO,
):
    task = await create_task(schema, uow)
    await enqueue_text2image_task(task.id, schema, client, context_client, uow)
    return task


@router.post("/text/text")
async def create_from_text_to_text(
    uow: TaskUoWDepend,
    client: OpenAIAdapterDepend,
    context_client: TaskContextAdapterDepend,
    schema: TaskCreateTextDTO
):
    task = await create_task(schema, uow)
    await enqueue_text2text_task(task.id, schema, client, context_client, uow)
    return task


@router.get("/statistics")
async def get_usage_statistics():
    # TODO Add usage saving after queued job finished
    # May be oncomplete in rq library
    pass


@router.get("/{task_id}", response_model=TaskReadDTO)
async def get_task_info(task_id: UUID, uow: TaskUoWDepend):
    task = await get_task(task_id, uow)
    return task


@router.get("/{task_id}/result", response_class=Response)
async def get_task_result():
    # TODO read file from system file storage
    pass
