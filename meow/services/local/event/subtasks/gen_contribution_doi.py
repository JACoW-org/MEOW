import logging as lg

from meow.tasks.local.doi.models import ContributionDOI, AuthorDOI
from meow.tasks.local.doi.utils import generate_doi_url

logger = lg.getLogger(__name__)

# TODO refactor: list of contributions will be passed instead of n arguments


async def gen_contribution_doi(event: dict, references: dict, doi_base_url: str, isbn: str, issn: str):
    ''''''

    dois: dict[str, ContributionDOI] = dict()

    for session in event.get('sessions', []):
        for contribution in session.get('contributions', []):

            doi_url = generate_doi_url(doi_base_url, event.get(
                'title', ''), contribution.get('code', ''))

            primary_authors = map(lambda author: AuthorDOI(
                first_name=author.get('first_name'),
                last_name=author.get('last_name'),
                affiliation=author.get('affiliation')), contribution.get('primary_authors'))

            # TODO probabilmente da event --> board che si occupa della gestione delle contributions
            editors = list()

            # TODO series aka "titolo" della conferenza

            # TODO start_page e number_of_pages da ricavare dal metadato del pdf

            data = ContributionDOI(
                title=contribution.get('title'),
                primary_authors=list(primary_authors),
                abstract=contribution.get('description'),
                references=contribution.get('references'),
                paper_url=contribution.get('url'),
                slides_url=contribution.get('url'),  # TODO missing data
                reference=references.get(contribution.get('code')),
                conference_code=event.get('title', ''),
                series=event.get('series', ''),    # TODO
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
                start_page=0,  # TODO
                number_of_pages=0,  # TODO
            )

            dois[contribution.get('code')] = data

    return dois
