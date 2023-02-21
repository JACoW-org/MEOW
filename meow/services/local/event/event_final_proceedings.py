import base64
import io
import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.final_proceedings.create_final_proceedings \
    import create_final_proceedings

from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin \
    import HugoFinalProceedingsPlugin

# TODO import from __init__
from meow.services.local.event.subtasks.gen_contribution_references \
    import gen_contribution_references

from meow.services.local.event.subtasks.gen_contribution_doi \
    import gen_contribution_doi


logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    # Adapt and refill event data: sessions, contributions, ...
    final_proceedings = await create_final_proceedings(event, cookies, settings)

    # Download pdf

    # Pdf metadata (keywords, n_pages, are_fonts_embedded, page_size)

    # Validation

    # Reference generation TODO refactor so that it updates each contribution's references
    references = await gen_contribution_references(event)

    # DOI generation
    dois = await gen_contribution_doi(event, references)

    # Contrib Groupby

    # PDF Editing

    # HTML + site
    static_site = await HugoFinalProceedingsPlugin(final_proceedings).run()

    # papers metadata
    papers_metadata = io.BytesIO()

    # final result
    yield await get_results(event, static_site, papers_metadata)


async def get_results(event: dict, static_site: io.BytesIO, papers_metadata: io.BytesIO) -> dict:
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
