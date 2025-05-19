from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork
from src.tasks.domain.entities import Task, TaskCreate


async def create_task(task_data: TaskCreateImageDTO | TaskCreateTextDTO, uow: ITaskUnitOfWork) -> Task:
    request = TaskCreate(**task_data.model_dump())
    async with uow:
        new_task = await uow.tasks.create(request)
        await uow.commit()
    return new_task
