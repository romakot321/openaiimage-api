from src.tasks.domain.entities import TaskStatisticsRemaining
from src.tasks.domain.interfaces.task_statistics_unit_of_work import ITaskStatisticsUnitOfWork


async def get_remaining(uow: ITaskStatisticsUnitOfWork) -> TaskStatisticsRemaining:
    async with uow:
        return await uow.statistics.get_remaining()
