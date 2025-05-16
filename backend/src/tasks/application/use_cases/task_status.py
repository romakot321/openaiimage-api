from uuid import UUID

from backend.src.tasks.domain.entities import Task
from backend.src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def get_task(task_id: UUID, uow: ITaskUnitOfWork) -> Task:
    return
