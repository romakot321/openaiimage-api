import abc

from src.tasks.domain.entities import TaskStatisticsRemaining


class ITaskStatisticsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_remaining(self) -> TaskStatisticsRemaining: ...

    @abc.abstractmethod
    async def store_remaining(self, remaining: TaskStatisticsRemaining) -> None: ...
