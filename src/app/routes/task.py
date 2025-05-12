from io import BytesIO
from PIL import Image
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, HTTPException
from fastapi.responses import Response
from uuid import UUID

from app.schemas.task import TaskCreateSchema, TaskSchema, TaskShortSchema
from app.services.context import ContextService
from app.services.task import TaskService
from . import validate_api_token

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.post("/image", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task_image2image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(),
    schema: TaskCreateSchema = Depends(TaskCreateSchema.as_form),
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    await service.add_request(task.id, schema, BytesIO(await file.read()))
    return task


@router.post("/text", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task_text2image(
    background_tasks: BackgroundTasks,
    schema: TaskCreateSchema,
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    await service.add_request(task.id, schema)
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
