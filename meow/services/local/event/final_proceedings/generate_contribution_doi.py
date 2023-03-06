import logging as lg
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import EventData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

from anyio import create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.tasks.local.doi.models import AuthorDOI, ContributionDOI
from meow.utils.datetime import format_datetime_full


logger = lg.getLogger(__name__)


async def generate_contribution_doi(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    total_files: int = len(proceedings_data.contributions)
    processed_files: int = 0

    if total_files == 0:
        raise Exception('no contributions found')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(6)

    results: dict[str, ContributionDOI] = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for contribution_data in proceedings_data.contributions:
                tg.start_soon(generate_doi_task, capacity_limiter, proceedings_data.event,
                              contribution_data, settings, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:
                    processed_files = processed_files + 1

                    # logger.info(result)

                    result_code: str = result.get('code', None)
                    result_value: ContributionDOI | None = result.get(
                        'value', None)

                    if result_value is not None:
                        results[result_code] = result_value

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    proceedings_data = refill_contribution_doi(proceedings_data, results)

    return proceedings_data


async def generate_doi_task(capacity_limiter: CapacityLimiter, event: EventData, contribution: ContributionData,
                            settings: dict, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        await res.send({
            "code": contribution.code,
            "value": await build_contribution_doi(event, contribution, settings)
        })


async def build_contribution_doi(event: EventData, contribution: ContributionData, settings: dict[str, str]):

    doi_base_url: str = settings.get(
        'doi_base_url', 'https://doi.org/10.18429')

    event_isbn: str = settings.get('isbn', '978-3-95450-227-1')
    event_issn: str = settings.get('issn', '2673-5490')

    primary_authors = [
        AuthorDOI(
            first_name=author.first,
            last_name=author.last,
            affiliation=author.affiliation
        )
        for author in contribution.primary_authors
    ]

    doi_data = ContributionDOI(
        title=contribution.title,
        primary_authors=primary_authors,
        abstract=contribution.description,
        # references=contribution.references,
        paper_url=contribution.url,
        slides_url=contribution.url,  # TODO missing data
        reference=contribution.reference,
        conference_code=event.title,
        # series=event.get(''),    # TODO
        venue=event.location,
        start_date=format_datetime_full(event.start),
        end_date=format_datetime_full(event.end),
        editors=[contribution.editor] if contribution.editor else [],
        isbn=event_isbn,
        issn=event_issn,
        reception_date=format_datetime_full(contribution.reception),
        acceptance_date=format_datetime_full(contribution.acceptance),
        issuance_date=format_datetime_full(contribution.issuance),
        doi_url=f"{doi_base_url}/JACoW-{event.title}-{contribution.code}",
        start_page=contribution.page,
        number_of_pages=contribution.metadata.get(
            'report', {}).get('page_count', 0)
        if contribution.metadata is not None else 0,
    )

    return doi_data


def refill_contribution_doi(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:

    start_page: int = 0

    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code
        try:
            if code in results and results[code] is not None:
                contribution_data.doi_data = results[code]
                contribution_data.doi_data.start_page = start_page
                start_page = start_page + contribution_data.doi_data.number_of_pages

        except Exception:
            logger.warning(f'No reference for contribution {code}')

    return proceedings_data
