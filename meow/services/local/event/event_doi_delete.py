

from asyncio import CancelledError
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from meow.models.infra.locks import RedisLock
from meow.services.local.event.common.adapting_final_proceedings import adapting_final_proceedings
from meow.services.local.event.common.collecting_contributions_and_files import collecting_contributions_and_files
from meow.services.local.event.common.collecting_sessions_and_attachments import collecting_sessions_and_attachments
from meow.services.local.event.doi.event_doi_delete import delete_contribution_doi


logger = lg.getLogger(__name__)


async def event_doi_delete(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:

            logger.debug(f"acquire_lock -> {lock.name}")

            async for r in _event_doi_delete(event, cookies, settings, lock):
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


async def _event_doi_delete(event: dict, cookies: dict, settings: dict, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_doi_delete - create_final_proceedings')

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_sessions_and_attachments',
        text="Collecting sessions and attachments"
    ))

    [sessions, attachments] = await collecting_sessions_and_attachments(event, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_contributions_and_files',
        text="Collecting contributions and files"
    ))

    [contributions] = await collecting_contributions_and_files(event, sessions, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='adapting_final_proceedings',
        text="Adapting final proceedings"
    ))

    final_proceedings = await adapting_final_proceedings(event, sessions, contributions, attachments, cookies, settings)

    logger.info('event_doi_delete - event_doi_delete - begin')

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='delete_contribution_doi',
        text="Delete contribution doi"
    ))

    # results = await delete_contribution_doi(final_proceedings, cookies, settings)
    
    async for result in delete_contribution_doi(final_proceedings, cookies, settings):
        yield dict(type='progress', value=dict(phase='doi_result', result=result))

    logger.info('event_doi_delete - event_doi_delete - end')

    yield dict(type='result', value={})
