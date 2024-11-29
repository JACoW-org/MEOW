""" Module responsible to generate the proceedings """

import logging as lg

from asyncio import CancelledError
from typing import AsyncGenerator
from redis.exceptions import LockError

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock


from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData)
from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsConfig, ProceedingsData)
from meow.services.local.event.final_proceedings.build_hep_payloads import (
    build_hep_payloads)
from meow.services.local.event.final_proceedings.copy_site_assets import (
    copy_html_partials, copy_inspirehep_jsonl)

from meow.services.local.event.final_proceedings.collecting_contributions_and_files import (
    collecting_contributions_and_files)
from meow.services.local.event.final_proceedings.collecting_sessions_and_materials import (
    collecting_sessions_and_materials)

from meow.services.local.event.common.adapting_final_proceedings import (
    adapting_proceedings)
from meow.services.local.event.common.validate_proceedings_data import (
    validate_proceedings_data)

from meow.services.local.event.final_proceedings.concat_contribution_papers import (
    concat_contribution_papers)
from meow.services.local.event.final_proceedings.copy_contribution_papers import (
    copy_contribution_papers)
from meow.services.local.event.final_proceedings.copy_contribution_slides import (
    copy_contribution_slides)
from meow.services.local.event.final_proceedings.copy_event_materials import (
    copy_event_materials)

from meow.services.local.event.final_proceedings.download_contributions_slides import (
    download_contributions_slides)
from meow.services.local.event.final_proceedings.download_event_materials import (
    download_event_materials)
from meow.services.local.event.final_proceedings.download_contributions_papers import (
    download_contributions_papers)

from meow.services.local.event.final_proceedings.generate_contribution_references import (
    generate_contribution_references)
from meow.services.local.event.final_proceedings.generate_contributions_groups import (
    generate_contributions_groups)
from meow.services.local.event.final_proceedings.generate_contribution_doi import (
    generate_dois)
from meow.services.local.event.final_proceedings.build_doi_payloads import (
    build_doi_payloads)
from meow.services.local.event.final_proceedings.manage_duplicates import (
    manage_duplicates)

from meow.services.local.event.final_proceedings.link_static_site import (
    clean_static_site, link_static_site)
from meow.services.local.event.final_proceedings.read_papers_metadata import (
    read_papers_metadata)
from meow.services.local.event.final_proceedings.write_papers_metadata import (
    write_papers_metadata)
from meow.services.local.event.final_proceedings.write_slides_metadata import (
    write_slides_metadata)

from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import (
    HugoProceedingsPlugin)
from meow.models.local.event.final_proceedings.client_log import ClientLog, ClientLogSeverity
from meow.app.errors.service_error import ProceedingsError


logger = lg.getLogger(__name__)


async def event_proceedings(event: dict, cookies: dict, settings: dict,
                            config: ProceedingsConfig) -> AsyncGenerator:
    """ event_proceedings """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:

            logger.debug(f"acquire_lock -> {lock.name}")

            async for r in _event_proceedings(event, cookies, settings, config, lock):
                yield r

            logger.debug(f"release_lock -> {lock.name}")

    except GeneratorExit:
        logger.error("Generator Exit")
    except CancelledError:
        logger.error("Task Cancelled")
    except LockError as le:
        logger.error("Lock error", exc_info=True)
        raise le
    except ProceedingsError as pe:
        async for r in handle_proceedings_error(pe):
            yield r
        raise pe
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


async def _event_proceedings(event: dict, cookies: dict, settings: dict,
                             config: ProceedingsConfig, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_proceedings - create_proceedings')

    """ """

    def filter_published_contributions(c: ContributionData) -> bool:
        if config.include_only_qa_green_contributions:
            return c.is_included_in_proceedings
        return c.is_included_in_prepress

    def filter_contributions_with_slides(c: ContributionData) -> bool:
        return config.include_event_slides and c.is_slides_included

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_sessions_and_materials',
        text="Collecting sessions and materials"
    ))

    # Blocking

    [sessions, materials] = await collecting_sessions_and_materials(event, cookies, settings)

    # log number of sessions and materials
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(sessions)} sessions.'
    ))

    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(materials)} materials.'
    ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_contributions_and_files',
        text="Collecting contributions and files"
    ))

    # Blocking

    [contributions] = await collecting_contributions_and_files(event, sessions, cookies, settings)

    # log number of contributions
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(contributions)} contributions.'
    ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='adapting_proceedings',
        text="Adapting proceedings"
    ))

    # Blocking

    # Deserialization process that builds a proceedings object that includes all the data of the conference
    proceedings = await adapting_proceedings(event, sessions, contributions, materials, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='clean_static_site',
        text='Clean Static site'
    ))

    await clean_static_site(proceedings, cookies, settings, config)

    """ """

    try:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='download_event_materials',
            text="Download event materials"
        ))

        # Blocking

        await download_event_materials(proceedings, cookies, settings)

    except Exception as ex:
        logger.error(ex, exc_info=True)

        # Produzione logs

        # Produzione result
        yield dict(type='result', value=dict(
            # metadata=metadata,
            # errors=errors
        ))

        # If blocking error
        return

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))

    # Blocking

    [proceedings, papers_data] = await download_contributions_papers(proceedings, cookies, settings,
                                                                     filter_published_contributions)

    # log number of files
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Downloaded {len(papers_data)} papers.'
    ))

    """ """

    if config.include_event_slides:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='download_contributions_slides',
            text="Download Contributions Slides"
        ))

        # Blocking

        [proceedings, slides_data] = await download_contributions_slides(proceedings, cookies, settings,
                                                                         filter_contributions_with_slides)

        # log number of files
        yield dict(type='log', value=ClientLog(
            severity=ClientLogSeverity.INFO,
            message=f'Downloaded {len(slides_data)} slides.'
        ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='read_papers_metadata',
        text='Read Papers Metadata'
    ))

    # Blocking

    await read_papers_metadata(proceedings, cookies, settings,
                               filter_published_contributions)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='validate_contributions_papers',
        text='Validate Contributions Papers'
    ))

    # Blocking if strict_pdf_check is True

    [metadata, errors] = await validate_proceedings_data(proceedings, cookies, settings,
                                                         filter_published_contributions)

    if len(errors) > 0:
        if config.strict_pdf_check:

            yield dict(type='log', value=ClientLog(
                severity=ClientLogSeverity.ERROR,
                message='Errors when validating proceedings data.'
            ))

            yield dict(type='result', value=dict(
                metadata=metadata,
                errors=errors
            ))

            return

        else:
            yield dict(type='log', value=ClientLog(
                severity=ClientLogSeverity.WARNING,
                message='Errors when validating proceedings data.'
            ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='extract_contribution_references',
        text='Extract Contribution References'
    ))

    # Blocking

    await generate_contribution_references(proceedings, cookies, settings, config,
                                           filter_published_contributions)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_dois',
        text='Generate DOIs'
    ))

    # Blocking

    await generate_dois(proceedings, cookies, settings, config,
                        filter_published_contributions)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='manage_duplicates',
        text='Managing duplicates'
    ))

    # Blocking

    await manage_duplicates(proceedings, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='write_papers_metadata',
        text='Write Papers Metadata'
    ))

    # Blocking

    await write_papers_metadata(proceedings, cookies, settings,
                                filter_published_contributions)
    """ """

    await extend_lock(lock)

    await write_slides_metadata(proceedings, cookies, settings,
                                filter_contributions_with_slides)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_contributions_groups',
        text='Generate Contributions Groups'
    ))

    await generate_contributions_groups(proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='concat_contribution_papers',
        text='Concat Contributions Papers'
    ))

    await concat_contribution_papers(proceedings, cookies, settings, config, filter_published_contributions)

    """ """

    if config.generate_doi_payload:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='generate_doi_payloads',
            text='Generate DOI payloads'
        ))

        # Blocking

        # generation of payloads for DOIs
        await build_doi_payloads(proceedings)

    """ """

    if config.generate_hep_payload:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='generate_inspirehep_payloads',
            text='Generate Inspirehep payloads'
        ))

        # Blocking

        # generation of payloads for DOIs
        await build_hep_payloads(proceedings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_site_pages',
        text='Generate Site Pages'
    ))

    plugin = HugoProceedingsPlugin(
        proceedings, cookies, settings, config)

    await plugin.run_prepare()
    await plugin.run_build()

    """ """

    await extend_lock(lock)

    logger.info('event_proceedings - copy_event_materials')

    yield dict(type='progress', value=dict(
        phase='copy_event_pdf',
        text='Copy event PDF'
    ))

    if config.generate_hep_payload:
        await copy_inspirehep_jsonl(proceedings, cookies, settings)

    await copy_html_partials(proceedings, cookies, settings)
    await copy_event_materials(proceedings, cookies, settings)
    await copy_contribution_papers(proceedings, cookies, settings,
                                   filter_published_contributions)

    if config.include_event_slides:
        await copy_contribution_slides(proceedings, cookies, settings,
                                       filter_contributions_with_slides)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_proceedings',
        text='Generate Proceedings'
    ))

    await plugin.generate()

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='link_static_site',
        text='Link Static site'
    ))

    await link_static_site(proceedings, cookies, settings, config)

    """ """

    await extend_lock(lock)

    logger.info('event_proceedings - get_proceedings')

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


async def handle_proceedings_error(error: ProceedingsError):
    """ Handle proceedings error """

    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.ERROR,
        message=str(error)
    ))

    # stop generation
    yield dict(type='error', value=error)
