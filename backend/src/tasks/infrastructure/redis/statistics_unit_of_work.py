from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.tasks.domain.interfaces.task_statistics_unit_of_work import ITaskStatisticsUnitOfWork

from src.redis.dependencies import get_redis_connection
from src.tasks.infrastructure.redis.repositories import RedisTaskStatisticsRepository


class RedisTaskStatisticsUnitOfWork(ITaskStatisticsUnitOfWork):
    def __init__(self, session_factory=get_redis_connection):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: Redis = self.session_factory()
        self.statistics = RedisTaskStatisticsRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()
