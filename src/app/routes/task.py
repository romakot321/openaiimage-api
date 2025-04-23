from fastapi import APIRouter, BackgroundTasks, Depends
from uuid import UUID

from app.schemas.task import TaskCreateSchema, TaskSchema, TaskSearchSchema, TaskShortSchema, TaskUpdateSchema
from app.services.task import TaskService
from . import validate_api_token

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.post("", response_model=TaskSchema, dependencies=[Depends(validate_api_token)])
async def create_task(
    schema: TaskCreateSchema,
    background_tasks: BackgroundTasks,
    service: TaskService = Depends(),
):
    task = await service.create(schema)
    background_tasks.add_task(service.send, task.id, schema)
    return task


@router.get("/{task_id}", response_model=TaskSchema, dependencies=[Depends(validate_api_token)])
async def get_task(task_id: UUID, service: TaskService = Depends()):
    return await service.get(task_id)


@router.get("", response_model=list[TaskShortSchema], dependencies=[Depends(validate_api_token)])
async def get_tasks_list(schema: TaskSearchSchema = Depends(), service: TaskService = Depends()):
    return await service.get_list(schema)


@router.patch("/{task_id}", response_model=TaskSchema, dependencies=[Depends(validate_api_token)])
async def update_task(schema: TaskUpdateSchema, task_id: UUID, service: TaskService = Depends()):
    return await service.update(task_id, schema)


@router.delete("/{task_id}", status_code=204, dependencies=[Depends(validate_api_token)])
async def delete_task(task_id: UUID, service: TaskService = Depends()):
    await service.delete(task_id)

