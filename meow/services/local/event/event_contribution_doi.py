import logging as lg

from typing import AsyncGenerator
from meow.tasks.local.doi.models import ContributionDOI, AuthorDOI
from meow.services.local.event.subtasks.gen_contribution_doi \
    import gen_contribution_doi

logger = lg.getLogger(__name__)

async def event_contribution_doi(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    ''''''

    doi_base_url: str = settings.get('doi-base-url', 'https://doi.org/10.18429')
    isbn: str = settings.get('isbn', '')
    issn: str = settings.get('issn', '')

    # references are empty when running the event
    dois = await gen_contribution_doi(event, dict(), doi_base_url, isbn, issn)

    yield dict(
        type='final',
        value=dois
    )
