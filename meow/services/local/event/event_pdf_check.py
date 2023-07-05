
from asyncio import CancelledError
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError
from meow.models.local.event.final_proceedings.client_log import ClientLog, ClientLogSeverity

from meow.models.local.event.final_proceedings.contribution_model import ContributionData

from meow.services.local.event.final_proceedings.collecting_contributions_and_files import (
    collecting_contributions_and_files)
from meow.services.local.event.final_proceedings.collecting_sessions_and_attachments import (
    collecting_sessions_and_attachments)
from meow.services.local.event.final_proceedings.download_contributions_papers import download_contributions_papers
from meow.services.local.event.common.validate_proceedings_data import validate_proceedings_data
from meow.services.local.event.common.adapting_final_proceedings import adapting_final_proceedings

from meow.services.local.event.check_pdf.read_papers_report import read_papers_report


logger = lg.getLogger(__name__)


async def event_pdf_check(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:
            async for r in _event_pdf_check(event, cookies, settings, lock):
                yield r

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

    return RedisLock(
        redis=dbs.redis_client,
        name=conf.REDIS_EVENT_LOCK_KEY(key),
        timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
        sleep=0.5,
        blocking=True,
        blocking_timeout=conf.REDIS_LOCK_BLOCKING_TIMEOUT_SECONDS,
        thread_local=True,
    )


async def extend_lock(lock: RedisLock) -> RedisLock:
    """ Reset lock timeout (conf.REDIS_LOCK_TIMEOUT_SECONDS) """

    await lock.reacquire()
    return lock


def callback(c: ContributionData) -> bool:
    return c.is_included_in_pdf_check


async def _event_pdf_check(event: dict, cookies: dict, settings: dict, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_check_pdf - create_final_proceedings')

    """ """

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

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))

    [final_proceedings, papers_data] = await download_contributions_papers(final_proceedings, cookies,
                                                                           settings, callback)

    # log number of files
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Downloaded {len(papers_data)} papers.'
    ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='read_papers_report',
        text='Read Papers Report'
    ))

    final_proceedings = await read_papers_report(final_proceedings, cookies, settings, callback)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='validate_contributions_papers',
        text='Validate Contributions Papers'
    ))

    [metadata, errors] = await validate_proceedings_data(final_proceedings, cookies, settings, callback)

    yield dict(type='result', value=dict(
        metadata=metadata,
        errors=errors
    ))
