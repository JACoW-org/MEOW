import logging as lg
from typing import Optional

from redis.asyncio.client import Redis
from redis.asyncio.lock import Lock
from redis.exceptions import LockError

logger = lg.getLogger(__name__)


class RedisLockList:
    """ """

    __locks: list[Lock] = []

    @classmethod
    def add_lock_to_static_list(cls, lock: Lock):
        """ """

        logger.error(f'>>>>>>>>>>> add_lock_to_static_list - {lock.name}')
        cls.__locks.append(lock)

    @classmethod
    def del_lock_to_static_list(cls, lock: Lock):
        """ """

        logger.error(f'>>>>>>>>>>> del_lock_to_static_list - {lock.name}')
        cls.__locks.remove(lock)

    @classmethod
    async def release_all_locks(cls):
        """ """

        logger.error(f'>>>>>>>>>>> release_all_locks - {cls.__locks}')

        for lock in cls.__locks:
            try:
                if lock is not None:
                    await lock.release()
                    logger.error(f'>>>>>>>>>>> release_all_locks - {lock.name} released')
            except Exception as e:
                logger.debug(e)


class RedisLock(Lock):
    """ """

    def __init__(
            self,
            redis: Redis,
            name: str,
            timeout: Optional[float] = None,
            sleep: float = 0.1,
            blocking: bool = True,
            blocking_timeout: Optional[float] = None,
            thread_local: bool = True,
    ):
        super(RedisLock, self).__init__(redis, name, timeout, sleep, blocking, blocking_timeout, thread_local)

    async def __aenter__(self):
        if await self.acquire():
            RedisLockList.add_lock_to_static_list(self)
            return self

        raise LockError("Unable to acquire lock")

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.release()
        RedisLockList.del_lock_to_static_list(self)
