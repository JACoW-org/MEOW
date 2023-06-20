from asyncio import CancelledError
import logging as lg

from typing import AsyncGenerator

from meow.app.config import conf
from meow.app.instances.databases import dbs
from meow.models.infra.locks import RedisLock

from redis.exceptions import LockError

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig, ProceedingsData

from meow.services.local.event.common.collecting_contributions_and_files import collecting_contributions_and_files
from meow.services.local.event.common.collecting_sessions_and_attachments import collecting_sessions_and_attachments

from meow.services.local.event.common.adapting_final_proceedings import adapting_final_proceedings
from meow.services.local.event.common.validate_proceedings_data import validate_proceedings_data

from meow.services.local.event.final_proceedings.concat_contribution_papers import concat_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_papers import copy_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_slides import copy_contribution_slides
from meow.services.local.event.final_proceedings.copy_event_attachments import copy_event_attachments

from meow.services.local.event.final_proceedings.download_contributions_slides import download_contributions_slides
from meow.services.local.event.final_proceedings.download_event_attachments import download_event_attachments
from meow.services.local.event.common.download_contributions_papers import download_contributions_papers

from meow.services.local.event.final_proceedings.generate_contribution_references import generate_contribution_references
from meow.services.local.event.final_proceedings.generate_contributions_groups import generate_contributions_groups
from meow.services.local.event.final_proceedings.generate_contribution_doi import generate_contribution_doi
from meow.services.local.event.final_proceedings.build_doi_payloads import build_doi_payloads
from meow.services.local.event.final_proceedings.manage_duplicates import manage_duplicates

from meow.services.local.event.final_proceedings.link_static_site import link_static_site
from meow.services.local.event.final_proceedings.read_papers_metadata import read_papers_metadata
from meow.services.local.event.final_proceedings.write_papers_metadata import write_papers_metadata

from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import HugoFinalProceedingsPlugin
from meow.models.local.event.final_proceedings.client_log import ClientLog, ClientLogSeverity
from meow.app.errors.service_error import ProceedingsError


logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict, config: FinalProceedingsConfig) -> AsyncGenerator:
    """ """

    try:
        event_id: str = event.get('id', '')

        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        async with acquire_lock(event_id) as lock:

            logger.debug(f"acquire_lock -> {lock.name}")

            async for r in _event_final_proceedings(event, cookies, settings, config, lock):
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



async def _event_final_proceedings(event: dict, cookies: dict, settings: dict, config: FinalProceedingsConfig, lock: RedisLock) -> AsyncGenerator:
    """ """

    logger.info('event_final_proceedings - create_final_proceedings')
    
    """ """
    
    def filter_contributions_pubblicated(c: ContributionData) -> bool:
        if config.include_only_qa_green_contributions: 
            return c.is_included_in_proceedings
        return c.is_included_in_prepress

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_sessions_and_attachments',
        text="Collecting sessions and attachments"
    ))
    
    ## Bloccante

    [sessions, attachments] = await collecting_sessions_and_attachments(event, cookies, settings)

    # log number of sessions and attachments
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(sessions)} sessions.'
    ))

    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(attachments)} attachments.'
    ))


    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='collecting_contributions_and_files',
        text="Collecting contributions and files"
    ))
    
    ## Bloccante

    [contributions] = await collecting_contributions_and_files(event, sessions, cookies, settings)

    # log number of contributions
    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.INFO,
        message=f'Found {len(contributions)} contributions.'
    ))

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='adapting_final_proceedings',
        text="Adapting final proceedings"
    ))
    
    ## Bloccante

    final_proceedings = await adapting_final_proceedings(event, sessions, contributions, attachments, cookies, settings)

    """ """
    
    try:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='download_event_attachments',
            text="Download event attachments"
        ))
        
        ## Bloccante

        await download_event_attachments(final_proceedings, cookies, settings)
    
    except Exception as ex:
        logger.error(ex, exc_info=True)
        
        ## Produzione logs
        
        ## Produzione result
        yield dict(type='result', value=dict(
            # metadata=metadata,
            # errors=errors
        ))
        
        ## Se l'errore è bloccante
        return
        
    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))
    
    ## Bloccante

    [final_proceedings, papers_data] = await download_contributions_papers(final_proceedings, cookies, settings, filter_contributions_pubblicated)

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
        
        ## Bloccante

        await download_contributions_slides(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='read_papers_metadata',
        text='Read Papers Metadata'
    ))
    
    ## Bloccante

    await read_papers_metadata(final_proceedings, cookies, settings, filter_contributions_pubblicated)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='validate_contributions_papers',
        text='Validate Contributions Papers'
    ))
    
    ## Bloccante il processo di validazione
    ## Mentre il risultato della validazione 
    ## è bloccante se strict_pdf_check

    [metadata, errors] = await validate_proceedings_data(final_proceedings, cookies, settings, filter_contributions_pubblicated)
        
    
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
    
    ## Bloccante

    await generate_contribution_references(final_proceedings, cookies, settings, config)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_contribution_doi',
        text='Generate Contribution DOI'
    ))
    
    ## Bloccante

    await generate_contribution_doi(final_proceedings, cookies, settings, config, filter_contributions_pubblicated)
    
    """ """
    
    if config.generate_doi_payload:

        await extend_lock(lock)

        yield dict(type='progress', value=dict(
            phase='generate_doi_payloads',
            text='Generate DOI payloads'
        ))
        
        ## Bloccante

        # generation of payloads for DOIs
        await build_doi_payloads(final_proceedings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='manage_duplicates',
        text='Managing duplicates'
    ))
    
    ## Bloccante

    await manage_duplicates(final_proceedings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='write_papers_metadata',
        text='Write Papers Metadata'
    ))

    ## Bloccante
    
    await write_papers_metadata(final_proceedings, cookies, settings, filter_contributions_pubblicated)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_contributions_groups',
        text='Generate Contributions Groups'
    ))

    await generate_contributions_groups(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='concat_contribution_papers',
        text='Concat Contributions Papers'
    ))

    await concat_contribution_papers(final_proceedings, cookies, settings, filter_contributions_pubblicated)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_site_pages',
        text='Generate Site Pages'
    ))

    plugin = HugoFinalProceedingsPlugin(final_proceedings, cookies, settings, config)

    await plugin.run_prepare()
    await plugin.run_build()

    """ """

    await extend_lock(lock)

    logger.info('event_final_proceedings - copy_event_attachments')

    yield dict(type='progress', value=dict(
        phase='copy_event_pdf',
        text='Copy event PDF'
    ))

    await copy_event_attachments(final_proceedings, cookies, settings)
    await copy_contribution_papers(final_proceedings, cookies, settings, filter_contributions_pubblicated)

    if config.include_event_slides:
        await copy_contribution_slides(final_proceedings, cookies, settings)

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='generate_final_proceedings',
        text='Generate Final Proceedings'
    ))

    await plugin.generate()

    """ """

    await extend_lock(lock)

    yield dict(type='progress', value=dict(
        phase='link_static_site',
        text='Link Static site'
    ))

    await link_static_site(final_proceedings, cookies, settings)

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

async def handle_proceedings_error(error: ProceedingsError):
    """ Handle proceedings error """

    yield dict(type='log', value=ClientLog(
        severity=ClientLogSeverity.ERROR,
        message=str(error)
    ))

    # stop generation
    yield dict(type='result', value=dict())

    raise error

