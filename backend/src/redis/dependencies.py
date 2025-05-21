from typing import AsyncIterator
from redis.asyncio import Redis
from .base import pool


async def get_redis_connection() -> Redis:
    client = Redis(connection_pool=pool)
    return client
