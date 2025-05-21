import redis.asyncio as redis
from src.core.config import settings

pool = redis.ConnectionPool(host=settings.REDIS_HOST, db=1)
