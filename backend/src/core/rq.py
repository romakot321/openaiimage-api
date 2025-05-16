from redis import Redis
from rq import Queue

from src.core.config import settings

task_queue = Queue(connection=Redis(host=settings.REDIS_HOST))
