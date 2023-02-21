import logging as lg

from typing import AsyncGenerator
from meow.tasks.local.doi.models import ContributionDOI, AuthorDOI
from meow.services.local.event.subtasks.gen_contribution_doi \
    import gen_contribution_doi

logger = lg.getLogger(__name__)

async def event_contribution_doi(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    ''''''

    # references are empty when running the event
    dois = gen_contribution_doi(event, dict())

    # DOI_BASE_URL = 'https://doi.org/10.18429'

    # for session in event.get('sessions', []):
    #     for contribution in session.get('contributions', []):

    #         primary_authors = map(lambda author: AuthorDOI(
    #             first_name=author.get('first_name'),
    #             last_name=author.get('last_name'),
    #             affiliation=author.get('affiliation')), contribution.get('primary_authors'))

    #         doi = f"{DOI_BASE_URL}/JACoW-{event.get('title')}-{contribution.get('code')}" # TODO improve

    #         reference_dict = dict() # TODO use generated reference from reference task

    #         editors = list()    # TODO probabilmente da event --> board che si occupa della gestione delle contributions

    #         # TODO series aka "titolo" della conferenza

    #         # TODO start_page e number_of_pages da ricavare dal metadato del pdf

    #         data = ContributionDOI(
    #             title=contribution.get('title'),
    #             primary_authors=list(primary_authors),
    #             abstract=contribution.get('description'),
    #             references=contribution.get('references'),
    #             paper_url=contribution.get('url'),
    #             slides_url=contribution.get('url'), # TODO missing data
    #             reference=reference_dict,
    #             conference_code=event.get('title'),
    #             series=event.get(''),    # TODO
    #             venue=event.get('location'),
    #             start_date=event.get('start_dt').get('date'),
    #             end_date=event.get('end_dt').get('date'),
    #             editors=editors,
    #             isbn=event.get('isbn', ''),
    #             issn=event.get('issn', ''),
    #             reception_date=contribution.get('reception_date', ''),
    #             acceptance_date=contribution.get('acceptance_date', ''),
    #             issuance_date=contribution.get('issuance_date', ''),
    #             doi=doi,
    #             start_page='',  # TODO
    #             number_of_pages=0, # TODO
    #         )

    #         yield dict(
    #             type='progress',
    #             value=data
    #         )

    yield dict(
        type='final',
        value=dois
    )
