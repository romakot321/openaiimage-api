from redis import Redis
from rq import Queue

from src.core.config import settings


class _PickableRedis(Redis):
    def __getstate__(self):
        print(self.__dict__)
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)


task_queue = Queue(connection=_PickableRedis(host=settings.REDIS_HOST, port=6379, db=0))
