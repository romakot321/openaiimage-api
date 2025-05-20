from fastapi import HTTPException
from redis.asyncio import Redis
from src.tasks.domain.entities import TaskStatisticsRemaining
from src.tasks.domain.interfaces.task_statistics_repository import ITaskStatisticsRepository


class RedisTaskStatisticsRepository(ITaskStatisticsRepository):
    remaining_key: str = "task.remaining"

    def __init__(self, connection: Redis) -> None:
        self.connection = connection

    async def get_remaining(self) -> TaskStatisticsRemaining:
        data = await self.connection.hgetall(self.remaining_key)
        if data is None:
            raise HTTPException(404, detail="Remaining data not stored yet. Please, wait for request")
        return TaskStatisticsRemaining.model_validate(data)

    async def store_remaining(self, remaining: TaskStatisticsRemaining) -> None:
        await self.connection.hmset(self.remaining_key, remaining.model_dump(mode="json"))
