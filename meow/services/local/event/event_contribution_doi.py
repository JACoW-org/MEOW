import logging as lg

from typing import AsyncGenerator

from meow.tasks.local.doi.models import ContributionDOI, AuthorDOI
from meow.tasks.local.doi.utils import generate_doi_external_url

logger = lg.getLogger(__name__)


# TODO REMOVE
async def event_contribution_doi(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    ''''''

    # doi_base_url: str = settings.get(
    #     'doi-base-url', 'https://doi.org/10.18429')

    doi_protocol = settings.get("doi_protocol", "https")
    doi_domain = settings.get("doi_domain", "doi.org")
    doi_context = settings.get("doi_context", "10.18429")
    doi_organization = settings.get("doi_organization", "JACoW")
    doi_conference = settings.get("doi_conference", "FEL2022")

    doi_user = settings.get("doi_user", "doi.user")
    doi_password = settings.get("doi_password", "doi.pass")

    # https://doi.org/10.18429/JACoW-PCaPAC2022
    doi_url = f'{doi_protocol}//{doi_domain}/{doi_context}/{doi_organization}-{doi_conference}'
    # DOI:10.18429/JACoW-PCaPAC2022
    doi_label = f'DOI:{doi_context}/{doi_organization}-{doi_conference}'

    isbn: str = settings.get('isbn', '')
    issn: str = settings.get('issn', '')
    issn: str = settings.get('booktitle_short', '')

    # references are empty when running the event
    dois = await gen_contribution_doi(event, dict(), doi_url, isbn, issn)

    yield dict(
        type='result',
        value=dois
    )


# TODO REMOVE
async def gen_contribution_doi(event: dict, references: dict, doi_base_url: str, isbn: str, issn: str):
    ''''''

    dois: dict[str, ContributionDOI] = dict()

    for session in event.get('sessions', []):
        for contribution in session.get('contributions', []):

            doi_url = ''
            doi_label = ''

            primary_authors = map(lambda author: AuthorDOI(
                first_name=author.get('first_name'),
                last_name=author.get('last_name'),
                affiliation=author.get('affiliation')), contribution.get('primary_authors'))

            editors = list()

            data = ContributionDOI(
                title=contribution.get('title'),
                abstract=contribution.get('description'),
                references=contribution.get('references'),
                paper_url=contribution.get('url'),
                slides_url=contribution.get('url'),
                reference=references.get(contribution.get('code')),
                conference_code=event.get('title', ''),
                series=event.get('series', ''),
                venue=event.get('location', ''),
                start_date=event.get('start_dt', {}).get('date', ''),
                end_date=event.get('end_dt', {}).get('date', ''),
                editors=editors,
                isbn=isbn,
                issn=issn,
                reception_date=contribution.get('reception_date', ''),
                acceptance_date=contribution.get('acceptance_date', ''),
                issuance_date=contribution.get('issuance_date', ''),
                doi_url=doi_url,
                doi_label=doi_label
            )

            dois[contribution.get('code')] = data

    return dois
