import abc

from src.tasks.domain.entities import TaskItem, TaskItemCreate


class ITaskItemRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, task_item: TaskItemCreate) -> TaskItem: ...

