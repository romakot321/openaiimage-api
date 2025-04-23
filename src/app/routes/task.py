from io import BytesIO
from PIL import Image
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from uuid import UUID

from app.schemas.task import TaskCreateSchema, TaskSchema, TaskShortSchema
from app.services.task import TaskService
from . import validate_api_token

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.post("", response_model=TaskShortSchema, dependencies=[Depends(validate_api_token)])
async def create_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(),
    schema: TaskCreateSchema = Depends(TaskCreateSchema.as_form),
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    image = BytesIO()
    Image.open(BytesIO(await file.read())).save(image, format="PNG", transparency=1)
    background_tasks.add_task(service.send, task.id, schema, image)
    return task


@router.get("/{task_id}", response_model=TaskSchema, dependencies=[Depends(validate_api_token)])
async def get_task(task_id: UUID, service: TaskService = Depends()):
    return await service.get(task_id)
