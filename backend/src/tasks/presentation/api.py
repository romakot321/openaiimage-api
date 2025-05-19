from io import BytesIO
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response

from src.core.auth import validate_api_token
from src.models.presentation.dependencies import ModelUoWDepend
from src.tasks.application.use_cases.task_status import get_task
from src.tasks.application.use_cases.task_result import get_task_image_result
from src.tasks.application.use_cases.task_create import create_task
from src.tasks.application.use_cases.task_queue import (
    enqueue_text2text_task,
    enqueue_text2image_task,
    enqueue_image2image_task
)
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO, TaskReadDTO
from src.tasks.presentation.dependencies import (
    OpenAIAdapterDepend,
    TaskContextAdapterDepend,
    TaskUoWDepend,
)

router = APIRouter(dependencies=[Depends(validate_api_token)])


@router.post("/image", response_model=TaskReadDTO)
async def create_from_image_to_image(
    uow: TaskUoWDepend,
    model_uow: ModelUoWDepend,
    client: OpenAIAdapterDepend,
    context_client: TaskContextAdapterDepend,
    image: UploadFile = File(),
    schema: TaskCreateImageDTO = Depends(TaskCreateImageDTO.as_form),
):
    task = await create_task(schema, uow)
    image_buffer = BytesIO(await image.read())
    await enqueue_image2image_task(task.id, schema, [image_buffer], client, context_client, uow, model_uow)
    return task


@router.post("/text", response_model=TaskReadDTO)
async def create_from_text_to_image(
    uow: TaskUoWDepend,
    model_uow: ModelUoWDepend,
    client: OpenAIAdapterDepend,
    context_client: TaskContextAdapterDepend,
    schema: TaskCreateImageDTO,
):
    task = await create_task(schema, uow)
    await enqueue_text2image_task(task.id, schema, client, context_client, uow, model_uow)
    return task


@router.post("/text/text", response_model=TaskReadDTO)
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
async def get_task_result(task_id: UUID, uow: TaskUoWDepend):
    buffer = await get_task_image_result(task_id, uow)
    return Response(content=buffer.read(), media_type="image/png")
