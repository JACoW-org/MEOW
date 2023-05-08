import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from anyio import create_task_group

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

from meow.services.local.event.common.collecting_contributions_and_files import collecting_contributions_and_files
from meow.services.local.event.common.collecting_sessions_and_attachments import collecting_sessions_and_attachments
from meow.services.local.event.common.create_final_proceedings import create_final_proceedings
from meow.services.local.event.common.validate_proceedings_data import validate_proceedings_data
from meow.services.local.event.common.download_contributions_papers import download_contributions_papers

from meow.services.local.event.final_proceedings.concat_contribution_papers import concat_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_papers import copy_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_slides import copy_contribution_slides
from meow.services.local.event.final_proceedings.copy_event_attachments import copy_event_attachments
from meow.services.local.event.final_proceedings.download_contributions_slides import download_contributions_slides

from meow.services.local.event.final_proceedings.download_event_attachments import download_event_attachments
from meow.services.local.event.final_proceedings.extract_contribution_references import extract_contribution_references
from meow.services.local.event.final_proceedings.generate_contribution_doi import generate_contribution_doi

from meow.services.local.event.final_proceedings.generate_contributions_groups import generate_contributions_groups
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import HugoFinalProceedingsPlugin
from meow.services.local.event.final_proceedings.link_static_site import link_static_site
from meow.services.local.event.final_proceedings.read_papers_metadata import read_papers_metadata
from meow.services.local.event.final_proceedings.write_papers_metadata import write_papers_metadata


logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:
            async for r in _event_final_proceedings(event, cookies, settings, lock):
                yield r

    except LockError as e:
        logger.error(e, exc_info=True)
        raise e
    except BaseException as e:
        logger.error(e, exc_info=True)
        raise e


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
    return c.is_included_in_proceedings


async def _event_final_proceedings(event: dict, cookies: dict, settings: dict, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_final_proceedings - create_final_proceedings')

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

    final_proceedings = await create_final_proceedings(event, sessions, contributions, attachments, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_event_attachments',
        text="Download event attachments"
    ))

    final_proceedings = await download_event_attachments(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))

    final_proceedings = await download_contributions_papers(final_proceedings, cookies, settings, callback)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_slides',
        text="Download Contributions Slides"
    ))

    final_proceedings = await download_contributions_slides(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='read_papers_metadata',
        text='Read Papers Metadata'
    ))

    final_proceedings = await read_papers_metadata(final_proceedings, cookies, settings, callback)

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

    # if len(errors) > 0:
    #     yield dict(type='result', value=dict(
    #         metadata=metadata,
    #         errors=errors
    #     ))
    #
    #     return

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='extract_contribution_references',
        text='Extract Contribution References'
    ))

    final_proceedings = await extract_contribution_references(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_contribution_doi',
        text='Generate Contribution Doi'
    ))

    final_proceedings = await generate_contribution_doi(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='extract_papers_metadata',
        text='Extract Papers Metadata'
    ))

    final_proceedings = await write_papers_metadata(final_proceedings, cookies, settings, callback)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_contributions_groups',
        text='Generate Contributions Groups'
    ))

    final_proceedings = await generate_contributions_groups(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='concat_contribution_papers',
        text='Concat Contributions Papers'
    ))

    final_proceedings = await concat_contribution_papers(final_proceedings, cookies, settings, callback)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_site_pages',
        text='Generate Site Pages'
    ))

    plugin = HugoFinalProceedingsPlugin(final_proceedings, cookies, settings)

    await plugin.run_prepare()
    await plugin.run_build()

    """ """

    await extend_lock(lock)

    logger.info('event_final_proceedings - copy_event_attachments')

    yield dict(type='progress', value=dict(
        phase='copy_event_pdf',
        text='Copy event PDF'
    ))

    async with create_task_group() as tg:
        tg.start_soon(copy_event_attachments,
                      final_proceedings, cookies, settings)
        tg.start_soon(copy_contribution_papers,
                      final_proceedings, cookies, settings, callback)
        tg.start_soon(copy_contribution_slides,
                      final_proceedings, cookies, settings)

    # # PDF Copy
    # final_proceedings = await copy_event_attachments(final_proceedings, cookies, settings)
    #
    # # PDF papers
    # final_proceedings = await copy_contribution_papers(final_proceedings, cookies, settings)
    #
    # # PDF slides
    # final_proceedings = await copy_contribution_slides(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_final_proceedings',
        text='Generate Final Proceedings'
    ))

    await plugin.generate()

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='compress_final_proceedings',
        text='Compress Final Proceedings'
    ))

    await plugin.compress()

    """ """

    final_proceedings = await link_static_site(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    logger.info('event_final_proceedings - get_final_proceedings')

    result = await get_final_proceedings(final_proceedings)

    yield result


async def get_final_proceedings(final_proceedings: ProceedingsData) -> dict:
    """ """

    event_code = final_proceedings.event.id
    event_name = final_proceedings.event.name
    event_title = final_proceedings.event.title
    event_path = final_proceedings.event.path

    return dict(
        type='result',
        value=dict(
            event_code=event_code,
            event_name=event_name,
            event_title=event_title,
            event_path=event_path
        )
    )
