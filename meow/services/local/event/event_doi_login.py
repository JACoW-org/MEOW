from asyncio import CancelledError
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from meow.services.local.event.doi.event_doi_login import http_datacite_login

from contextvars import Token
from meow.utils.logger import event_id_var

logger = lg.getLogger(__name__)


async def event_doi_login(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    token: Token = None

    try:
        event_id: str = event.get("id", "")

        if not event_id or event_id == "":
            raise BaseException("Invalid event id")

        token = event_id_var.set(event_id)

        async with acquire_lock(event_id) as lock:
            logger.debug(f"acquire_lock -> {lock.name}")

            async for r in _event_doi_login(
                event,
                cookies,
                settings,
                lock,
            ):
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
    finally:
        event_id_var.reset(token)


def acquire_lock(key: str) -> RedisLock:
    """Create event lock"""

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
    """Reset lock timeout (conf.REDIS_LOCK_TIMEOUT_SECONDS)"""

    await lock.reacquire()
    return lock


async def _event_doi_login(
    event: dict, cookies: dict, settings: dict, lock: RedisLock
) -> AsyncGenerator:
    """ """

    logger.info("event_doi_login - start")

    value = await http_datacite_login(settings=settings)

    logger.info("event_doi_login - end")

    yield dict(type="result", value=value)
