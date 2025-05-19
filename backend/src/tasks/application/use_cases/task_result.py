from typing import BinaryIO
from uuid import UUID

from fastapi import HTTPException

from src.core.filesystem_storage import storage
from src.tasks.domain.interfaces.task_uow import ITaskUnitOfWork


async def get_task_image_result(task_id: UUID, uow: ITaskUnitOfWork) -> BinaryIO:
    async with uow:
        task = await uow.tasks.get_by_pk(task_id)
    if not task.items:
        raise HTTPException(404)
    filename = str(task_id)
    return storage.open(filename)
