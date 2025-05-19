from uuid import UUID

from src.tasks.domain.entities import Task
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def get_task(task_id: UUID, uow: ITaskUnitOfWork) -> Task:
    async with uow:
        task = await uow.tasks.get_by_pk(task_id)
    return task
