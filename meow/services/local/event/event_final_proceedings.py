import base64
import io
import logging as lg

from typing import AsyncGenerator
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

from meow.services.local.event.final_proceedings.collecting_contributions_and_files import collecting_contributions_and_files
from meow.services.local.event.final_proceedings.collecting_sessions_and_attachments import collecting_sessions_and_attachments
from meow.services.local.event.final_proceedings.concat_contribution_papers import concat_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_papers import copy_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_slides import copy_contribution_slides
from meow.services.local.event.final_proceedings.copy_event_attachments import copy_event_attachments
from meow.services.local.event.final_proceedings.download_contributions_slides import download_contributions_slides

from meow.services.local.event.final_proceedings.download_event_attachments import download_event_attachments
from meow.services.local.event.final_proceedings.download_contributions_papers import download_contributions_papers
from meow.services.local.event.final_proceedings.extract_contribution_references import extract_contribution_references
from meow.services.local.event.final_proceedings.generate_contribution_doi import generate_contribution_doi

from meow.services.local.event.final_proceedings.create_final_proceedings import create_final_proceedings
from meow.services.local.event.final_proceedings.generate_contributions_groups import generate_contributions_groups
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import HugoFinalProceedingsPlugin
from meow.services.local.event.final_proceedings.link_static_site import link_static_site
from meow.services.local.event.final_proceedings.read_papers_metadata import read_papers_metadata
from meow.services.local.event.final_proceedings.validate_proceedings_data import validate_proceedings_data
from meow.services.local.event.final_proceedings.write_papers_metadata import write_papers_metadata


logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    logger.info('event_final_proceedings - create_final_proceedings')

    """ """

    logger.info('event_final_proceedings - collecting_sessions_and_attachments')

    yield dict(type='progress', value=dict(
        phase='collecting_sessions_and_attachments',
        text="Collecting sessions and attachments"
    ))

    [sessions, attachments] = await collecting_sessions_and_attachments(event, cookies, settings)

    """ """

    logger.info('event_final_proceedings - collecting_contributions_and_files')

    yield dict(type='progress', value=dict(
        phase='collecting_contributions_and_files',
        text="Collecting contributions and files"
    ))

    [contributions] = await collecting_contributions_and_files(event, sessions, cookies, settings)

    """ """

    logger.info('event_final_proceedings - adapting_final_proceedings')

    yield dict(type='progress', value=dict(
        phase='adapting_final_proceedings',
        text="Adapting final proceedings"
    ))

    final_proceedings = await create_final_proceedings(event, sessions, contributions, attachments, cookies, settings)

    """ """

    logger.info('event_final_proceedings - download_event_attachments')

    yield dict(type='progress', value=dict(
        phase='download_event_attachments',
        text="Download event attachments"
    ))

    # Download attachments
    final_proceedings = await download_event_attachments(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - download_contributions_papers')

    yield dict(type='progress', value=dict(
        phase='download_contributions_papers',
        text="Download Contributions Papers"
    ))

    # Download papers
    final_proceedings = await download_contributions_papers(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - download_contributions_papers')

    yield dict(type='progress', value=dict(
        phase='download_contributions_slides',
        text="Download Contributions Slides"
    ))

    # Download papers
    final_proceedings = await download_contributions_slides(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - read_papers_metadata')

    yield dict(type='progress', value=dict(
        phase='read_papers_metadata',
        text='Read Papers Metadata'
    ))

    # Pdf metadata (keywords, n_pages, are_fonts_embedded, page_size)
    final_proceedings = await read_papers_metadata(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - validate_events_data')

    yield dict(type='progress', value=dict(
        phase='validate_contributions_papers',
        text='Validate Contributions Papers'
    ))

    # TODO: Validation
    final_proceedings = await validate_proceedings_data(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - extract_contribution_references')

    yield dict(type='progress', value=dict(
        phase='extract_contribution_references',
        text='Extract Contribution References'
    ))

    # Generate contribution references
    final_proceedings = await extract_contribution_references(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - generate_contribution_doi')

    yield dict(type='progress', value=dict(
        phase='generate_contribution_doi',
        text='Generate Contribution Doi'
    ))

    # DOI generation
    final_proceedings = await generate_contribution_doi(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - write_papers_metadata')

    yield dict(type='progress', value=dict(
        phase='extract_papers_metadata',
        text='Extract Papers Metadata'
    ))

    # Write metadata and frames
    final_proceedings = await write_papers_metadata(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    yield dict(type='progress', value=dict(
        phase='concat_contributions_papers',
        text='Concat Contributions Papers'
    ))

    # Concat Pdf
    final_proceedings = await concat_contribution_papers(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - generate_contributions_groups')

    yield dict(type='progress', value=dict(
        phase='generate_contributions_groups',
        text='Generate Contributions Groups'
    ))

    # Contrib Groupby
    final_proceedings = await generate_contributions_groups(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - generate_final_proceedings')

    yield dict(type='progress', value=dict(
        phase='generate_final_proceedings',
        text='Generate Final Proceedings'
    ))

    # HTML + site

    plugin = HugoFinalProceedingsPlugin(final_proceedings, cookies, settings)

    await plugin.run_prepare()

    await plugin.run_build()

    """ """

    logger.info('event_final_proceedings - copy_event_attachments')

    yield dict(type='progress', value=dict(
        phase='copy_event_attachments',
        text='Copy Event Attachments'
    ))

    # PDF Copy
    final_proceedings = await copy_event_attachments(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - copy_contribution_papers')

    yield dict(type='progress', value=dict(
        phase='copy_contributions_papers',
        text='Copy Contributions Papers'
    ))

    # PDF papers
    final_proceedings = await copy_contribution_papers(final_proceedings, cookies, settings)

    """ """

    logger.info('event_final_proceedings - copy_contribution_slides')

    yield dict(type='progress', value=dict(
        phase='copy_contribution_slides',
        text='Copy Contributions Slides'
    ))

    # PDF slides
    final_proceedings = await copy_contribution_slides(final_proceedings, cookies, settings)

    """ """

    yield dict(type='progress', value=dict(
        phase='compress_final_proceedings',
        text='Compress Final Proceedings'
    ))

    logger.info('event_final_proceedings - plugin.run_pack')

    await plugin.generate()

    static_site = io.BytesIO()  # await plugin.run_pack()

    """ """

    # Link site
    final_proceedings = await link_static_site(final_proceedings, cookies, settings)

    # papers metadata
    papers_metadata = io.BytesIO()

    """ """

    logger.info('event_final_proceedings - get_final_proceedings')

    # TODO: final proceedings file url to download
    result = await get_final_proceedings(final_proceedings, static_site, papers_metadata)

    yield result


async def get_final_proceedings(final_proceedings: ProceedingsData, proceedings: io.BytesIO, metadata: io.BytesIO) -> dict:
    """ """

    event_code = final_proceedings.event.id
    event_title = final_proceedings.event.title

    return dict(
        type='final',
        value=dict(
            final_proceedings=dict(
                base64=base64.b64encode(
                    proceedings.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_final_proceedings.7z"
            ),
            papers_metadata=dict(
                base64=base64.b64encode(metadata.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_papers_metadata.7z"
            )
        )
    )
