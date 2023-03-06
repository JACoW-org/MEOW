import base64
import io
import logging as lg

from typing import AsyncGenerator
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.final_proceedings.concat_contribution_papers import concat_contribution_papers
from meow.services.local.event.final_proceedings.copy_contribution_papers import copy_contribution_papers

from meow.services.local.event.final_proceedings.download_contributions_papers import download_contributions_papers
from meow.services.local.event.final_proceedings.extract_contribution_references import extract_contribution_references
from meow.services.local.event.final_proceedings.extract_papers_metadata import extract_papers_metadata
from meow.services.local.event.final_proceedings.generate_contribution_doi import generate_contribution_doi

from meow.services.local.event.final_proceedings.create_final_proceedings \
    import create_final_proceedings
from meow.services.local.event.final_proceedings.generate_contributions_groups import generate_contributions_groups
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin \
    import HugoFinalProceedingsPlugin
from meow.services.local.event.final_proceedings.link_static_site import link_static_site
from meow.services.local.event.final_proceedings.refill_papers_metadata import refill_papers_metadata
from meow.services.local.event.final_proceedings.validate_proceedings_data \
    import validate_proceedings_data



logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """
    
    logger.info('event_final_proceedings - create_final_proceedings')

    # Adapt and refill event data: sessions, contributions, ...
    final_proceedings = await create_final_proceedings(event, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - download_contributions_papers')

    yield dict(type='progress', value=dict(phase='download_contributions_papers'))
    
    # Download pdf
    final_proceedings = await download_contributions_papers(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - extract_papers_metadata')    

    yield dict(type='progress', value=dict(phase='extract_papers_metadata'))
    
    # Pdf metadata (keywords, n_pages, are_fonts_embedded, page_size)
    final_proceedings = await extract_papers_metadata(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - validate_events_data')
    
    yield dict(type='progress', value=dict(phase='validate_events_data'))
    
    # TODO: Validation
    final_proceedings = await validate_proceedings_data(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - concat_contribution_papers')    

    yield dict(type='progress', value=dict(phase='concat_contribution_papers'))
    
    # Concat Pdf
    final_proceedings = await concat_contribution_papers(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - extract_contribution_references')
    
    yield dict(type='progress', value=dict(phase='extract_contribution_references'))

    # Generate contribution references
    final_proceedings = await extract_contribution_references(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - generate_contribution_doi')
    
    yield dict(type='progress', value=dict(phase='generate_contribution_doi'))

    # DOI generation
    final_proceedings = await generate_contribution_doi(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - generate_contributions_groups')
    
    yield dict(type='progress', value=dict(phase='generate_contributions_groups'))
    
    # Contrib Groupby
    final_proceedings = await generate_contributions_groups(final_proceedings, cookies, settings)
    
    

    logger.info('event_final_proceedings - refill_papers_metadata')
    
    yield dict(type='progress', value=dict(phase='refill_papers_metadata'))

    # TODO: PDF Editing????
    final_proceedings = await refill_papers_metadata(final_proceedings, cookies, settings)
    
    
    
    logger.info('event_final_proceedings - gen_final_proceedings')
    
    yield dict(type='progress', value=dict(phase='gen_final_proceedings'))

    # HTML + site
    
    plugin = HugoFinalProceedingsPlugin(final_proceedings)
        
    await plugin.run_prepare()
    
    await plugin.run_build()
    
    
    
    logger.info('event_final_proceedings - copy_contribution_papers')
    
    yield dict(type='progress', value=dict(phase='copy_contribution_papers'))

    # PDF Copy
    final_proceedings = await copy_contribution_papers(final_proceedings, cookies, settings)
    
    
      
    yield dict(type='progress', value=dict(phase='plugin.run_pack'))
    
    logger.info('event_final_proceedings - plugin.run_pack')
    
    await plugin.generate()
    
    static_site = io.BytesIO() # await plugin.run_pack()
    
    
    # Link site
    final_proceedings = await link_static_site(final_proceedings, cookies, settings)

    # papers metadata
    papers_metadata = io.BytesIO()
    
    
    
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
                base64=base64.b64encode(proceedings.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_final_proceedings.7z"
            ),
            papers_metadata=dict(
                base64=base64.b64encode(metadata.getvalue()).decode('utf-8'),
                filename=f"{event_code}_{event_title}_papers_metadata.7z"
            )
        )
    )
