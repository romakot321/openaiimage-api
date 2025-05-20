import abc

from src.tasks.domain.interfaces.task_statistics_repository import ITaskStatisticsRepository



class ITaskStatisticsUnitOfWork(abc.ABC):
    statistics: ITaskStatisticsRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        pass
