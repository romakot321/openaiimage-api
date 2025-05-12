from io import BytesIO
from PIL import Image
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, HTTPException
from fastapi.responses import Response
from uuid import UUID

from app.schemas.task import TaskImageCreateSchema, TaskSchema, TaskShortSchema, TaskStatisticsSchema, TaskTextCreateSchema
from app.services.context import ContextService
from app.services.task import TaskService
from . import validate_api_token

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.get("/statistics", response_model=TaskStatisticsSchema, dependencies=[Depends(validate_api_token)])
def get_api_statistics(service: TaskService = Depends()):
    return service.get_statistics()


@router.post("/image", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task_image2image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(),
    schema: TaskImageCreateSchema = Depends(TaskImageCreateSchema.as_form),
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    await service.add_request(task.id, schema, BytesIO(await file.read()))
    return task


@router.post("/text", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task_text2image(
    background_tasks: BackgroundTasks,
    schema: TaskImageCreateSchema,
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    await service.add_request(task.id, schema)
    return task


@router.post("/text/text", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task_text2text(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(),
    schema: TaskTextCreateSchema = Depends(TaskTextCreateSchema.as_form),
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    await service.add_request(task.id, schema, BytesIO(await file.read()))
    return task


@router.get("/{task_id}", response_model=TaskSchema, dependencies=[Depends(validate_api_token)])
async def get_task(task_id: UUID, service: TaskService = Depends()):
    return await service.get(task_id)


@router.get("/{task_id}/result", response_class=Response)
def get_task_result(task_id: UUID, service: TaskService = Depends()):
    content = service.get_result(task_id)
    if content is None:
        raise HTTPException(404)
    return Response(content=content, media_type="image/png")
