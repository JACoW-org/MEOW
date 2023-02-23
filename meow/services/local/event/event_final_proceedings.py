import base64
import io
import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.final_proceedings.download_contributions_papers import download_contributions_papers
from meow.services.local.event.final_proceedings.extract_contribution_references import extract_contribution_references
from meow.services.local.event.final_proceedings.extract_papers_metadata import extract_papers_metadata
from meow.services.local.event.final_proceedings.generate_contribution_doi import generate_contribution_doi

from meow.services.local.event.final_proceedings.create_final_proceedings \
    import create_final_proceedings
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin \
    import HugoFinalProceedingsPlugin
from meow.services.local.event.final_proceedings.validate_proceedings_data \
    import validate_proceedings_data



logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """
    
    logger.info('event_final_proceedings - create_final_proceedings')

    # Adapt and refill event data: sessions, contributions, ...
    final_proceedings = await create_final_proceedings(event, cookies, settings)
    
    logger.info('event_final_proceedings - download_contributions_papers')

    # Download pdf
    final_proceedings = await download_contributions_papers(final_proceedings, cookies, settings)
    
    logger.info('event_final_proceedings - extract_papers_metadata')
    
    # Pdf metadata (keywords, n_pages, are_fonts_embedded, page_size)
    final_proceedings = await extract_papers_metadata(final_proceedings, cookies, settings)
    
    logger.info('event_final_proceedings - validate_events_data')
    
    # TODO: Validation
    final_proceedings = await validate_proceedings_data(final_proceedings, cookies, settings)
    
    logger.info('event_final_proceedings - extract_contribution_references')

    # Generate contribution references
    final_proceedings = await extract_contribution_references(final_proceedings, cookies, settings)
    
    logger.info('event_final_proceedings - gen_contribution_doi')

    # DOI generation
    final_proceedings = await generate_contribution_doi(final_proceedings, cookies, settings)

    # Contrib Groupby
    
    logger.info('event_final_proceedings - gen_contributions_groups')

    # PDF Editing
    
    logger.info('event_final_proceedings - gen_final_proceedings')

    # HTML + site
    static_site = await HugoFinalProceedingsPlugin(final_proceedings).run()
    
    logger.info('event_final_proceedings - gen_papers_metadata')

    # papers metadata
    papers_metadata = io.BytesIO()
    
    logger.info('event_final_proceedings - get_final_proceedings')

    # final result
    yield await get_final_proceedings(event, static_site, papers_metadata)


async def get_final_proceedings(event: dict, static_site: io.BytesIO, papers_metadata: io.BytesIO) -> dict:
    """ """

    event_code = event.get('id', '')
    event_title = event.get('title', '')

    return dict(
        type='final',
        value=dict(
            final_proceedings=dict(
                b64=base64.b64encode(static_site.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_final_proceedings.7z"
            ),
            papers_metadata=dict(
                b64=base64.b64encode(
                    papers_metadata.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_papers_metadata.7z"
            )
        )
    )
