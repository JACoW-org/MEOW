import logging as lg

from meow.app.config import conf
from meow.app.instances.databases import dbs

from typing import AsyncGenerator
from meow.models.infra.locks import RedisLock

from meow.services.local.event.event_final_proceedings \
    import event_final_proceedings

from meow.tasks.infra.abstract_task import AbstractTask
from redis.exceptions import LockError

logger = lg.getLogger(__name__)


class EventZipTask(AbstractTask):
    """ EventZipTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        try:
            async with acquire_lock() as lock:

                event: dict = params.get('event', dict())
                cookies: dict = params.get('cookies', dict())
                settings: dict = params.get('settings', dict())
                
                async for r in event_final_proceedings(event, cookies, settings):
                    yield r

        except LockError as e:
            logger.error(e, exc_info=True)
        except Exception as e:
            logger.error(e, exc_info=True)

def acquire_lock() -> RedisLock:
    return RedisLock(
        redis=dbs.redis_client,
        name=conf.REDIS_GLOBAL_LOCK_KEY,
        timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
        sleep=0.1,
        blocking=True,
        blocking_timeout=5*60*1000,
        thread_local=True,
    )
