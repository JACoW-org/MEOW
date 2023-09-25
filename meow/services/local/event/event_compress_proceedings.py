from asyncio import CancelledError
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.common.adapting_final_proceedings import adapting_proceedings
from meow.services.local.event.final_proceedings.compress_final_proceedings import compress_proceedings


logger = lg.getLogger(__name__)


async def event_compress_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:

            logger.debug(f"acquire_lock -> {lock.name}")

            async for r in _event_compress_proceedings(event, cookies, settings, lock):
                yield r

            logger.debug(f"release_lock -> {lock.name}")

    except GeneratorExit:
        logger.error("Generator Exit")
    except CancelledError:
        logger.error("Task Cancelled")
    except LockError as le:
        logger.error("Lock error", exc_info=True)
        raise le
    except BaseException as be:
        logger.error("Generic error", exc_info=True)
        raise be


def acquire_lock(key: str) -> RedisLock:
    """ Create event lock """

    redis_lock = RedisLock(
        redis=dbs.redis_client,
        name=conf.REDIS_EVENT_LOCK_KEY(key),
        timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
        sleep=0.5,
        blocking=True,
        blocking_timeout=conf.REDIS_LOCK_BLOCKING_TIMEOUT_SECONDS,
        thread_local=True,
    )

    return redis_lock


async def extend_lock(lock: RedisLock) -> RedisLock:
    """ Reset lock timeout (conf.REDIS_LOCK_TIMEOUT_SECONDS) """

    await lock.reacquire()
    return lock


async def _event_compress_proceedings(event: dict, cookies: dict, settings: dict, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('_event_compress_proceedings - _event_compress_proceedings')

    """ """

    sessions = []
    contributions = []
    materials = []

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='adapting_proceedings',
        text="Adaptin proceedings"
    ))

    proceedings = await adapting_proceedings(event, sessions, contributions, materials, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='compress_static_site',
        text='Compress Static site'
    ))

    await compress_proceedings(proceedings, cookies, settings)

    result = await get_proceedings(proceedings)

    yield result


async def get_proceedings(proceedings: ProceedingsData) -> dict:
    """ """

    event_code = proceedings.event.id
    event_name = proceedings.event.name
    event_title = proceedings.event.title
    event_path = proceedings.event.path

    return dict(
        type='result',
        value=dict(
            event_code=event_code,
            event_name=event_name,
            event_title=event_title,
            event_path=event_path
        )
    )
