import logging as lg
import datetime

from typing import Callable
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import EventData, PersonData

from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig, ProceedingsData

from anyio import create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.tasks.local.doi.models import AuthorDOI, ContributionDOI, EditorDOI
from meow.tasks.local.doi.utils import (generate_doi_external_label, generate_doi_external_url,
                                        generate_doi_identifier, generate_doi_internal_url,
                                        generate_doi_landing_page_url, generate_doi_name,
                                        generate_doi_path)

from meow.utils.datetime import (
    format_datetime_doi_iso, format_datetime_full, format_datetime_range_doi, format_datetime_doi)
from meow.utils.serialization import json_decode
from meow.models.local.event.final_proceedings.event_factory import event_person_factory


logger = lg.getLogger(__name__)


async def generate_dois(proceedings_data: ProceedingsData, cookies: dict, settings: dict,
                        config: FinalProceedingsConfig, callable: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - generate_contribution_doi')

    contributions = [
        c for c in proceedings_data.contributions if callable(c) and c.page > 0]

    total_files: int = len(contributions)
    processed_files: int = 0

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(8)

    conference_doi = dict()
    results: dict[str, ContributionDOI] = dict()

    async with create_task_group() as tg:
        async with send_stream:

            tg.start_soon(generate_conference_doi_task, capacity_limiter, proceedings_data,
                          settings, config, send_stream.clone())

            for contribution_data in contributions:
                tg.start_soon(generate_contribution_doi_task, capacity_limiter, proceedings_data.event,
                              contribution_data, settings, config, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:

                    result_type: str = result.get('type', None)

                    if result_type == 'conference':
                        conference_doi = result.get('value')
                    elif result_type == 'contribution':
                        processed_files = processed_files + 1

                        result_code: str = result.get('code', None)
                        result_value: ContributionDOI | None = result.get(
                            'value', None)

                        if result_value is not None:
                            results[result_code] = result_value

                        if processed_files >= total_files:
                            # close stream only when all contributions have been processed
                            receive_stream.close()
                    else:
                        logger.error(
                            f'Received unexpected result type: {result_type}')

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    proceedings_data.conference_doi = conference_doi

    proceedings_data = refill_contribution_doi(
        proceedings_data, results, callable)

    return proceedings_data


async def generate_conference_doi_task(capacity_limiter: CapacityLimiter,
                                       proceedings_data: ProceedingsData,
                                       settings: dict,
                                       config: FinalProceedingsConfig,
                                       res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        await res.send({
            'type': 'conference',
            'value': await build_conference_doi(proceedings_data, settings, config)
        })


async def build_conference_doi(proceedings_data: ProceedingsData, settings: dict, config: FinalProceedingsConfig):
    """ """

    doi_identifier: str = generate_doi_identifier(
        context=settings.get('doi_context', '10.18429'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY')
    )

    doi_url: str = generate_doi_external_url(
        protocol=settings.get('doi_proto', 'https'),
        domain=settings.get('doi_domain', 'doi.org'),
        context=settings.get('doi_context', 'CONF-CTX'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY')
    ) if config.generate_external_doi_url else generate_doi_internal_url(
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY')
    )

    doi_landing_page: str = generate_doi_landing_page_url(
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY')
    )

    editors_dict_list = json_decode(settings.get(
        'editorial_json', '{}'))

    editors: list[PersonData] = [
        event_person_factory(person)
        for person in editors_dict_list
    ]

    conference_doi = {
        'id': doi_identifier,
        'type': 'dois',
        'doi': doi_identifier,
        'identifiers': [{
            'identifier': doi_url,
            'identifierType': 'DOI'
        }],
        'creators': [],
        'titles': [{
            'title': settings.get('booktitle_long', ''),
            'lang': 'en-us'
        }],
        'publisher': 'JACoW Publishing',
        'publicationYear': datetime.date.today().year,
        'subjects': [{
            'subject': 'Accelerator Physics',
            'lang': 'en-us'
        }],
        'contributors': [{
            'name': f'{editor.last},{editor.first}',
            'nameType': 'Personal',
            'affiliation': [{
                'name': editor.affiliation
            }],
            'contributorType': 'Editor',
            'nameIdentifiers': [{
                'nameIdentifier': index,
                'schemeUri': 'https://jacow.org',
                'nameIdentifierScheme': 'JACoW-ID'
            }]
        } for index, editor in enumerate(editors)],
        'dates': [],
        'language': 'en-us',
        'types': {
            'resourceTypeGeneral': 'ConferenceProceeding',
            'resourceType': '',
            'ris': 'CONF',
            'bibtex': 'misc',
            'citeproc': 'article',
            'schemeOrg': 'Periodical'
        },
        'relatedIdentifiers': [{
            'relatedIdentifier': settings.get('isbn', ''),
            'relatedIdentifierType': 'ISBN',
            'relationType': 'IsPartOf'
        }, {
            'relatedIdentifier': settings.get('issn', ''),
            'relatedIdentifierType': 'ISSN',
            'relationType': 'IsPartOf'
        }],
        'sizes': [],
        'formats': [],
        'rightsList': [{
            'rights': 'Creative Commons Attribution 4.0 International',
            'rightsUri': 'https://creativecommons.org/licenses/by/4.0/legalcode',
            'lang': 'en-us',
            'schemeUri': 'https://spdx.org/licenses/',
            'rightsIdentifier': 'cc-by-4.0',
            'rightsIdentifierScheme': 'SPDX'
        }],
        'descriptions': [],
        'url': doi_landing_page,
        'schemaVersion': 'http://datacite.org/schema/kernel-4'
    }

    return conference_doi


async def generate_contribution_doi_task(capacity_limiter: CapacityLimiter, event: EventData,
                                         contribution: ContributionData, settings: dict,
                                         config: FinalProceedingsConfig,
                                         res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        await res.send({
            'type': 'contribution',
            'code': contribution.code,
            'value': await build_contribution_doi(
                event, contribution, settings, config)
        })


async def build_contribution_doi(event: EventData, contribution: ContributionData,
                                 settings: dict[str, str], config: FinalProceedingsConfig):

    doi_label: str = generate_doi_external_label(
        protocol=settings.get('doi_proto', 'https'),
        domain=settings.get('doi_domain', 'doi.org'),
        context=settings.get('doi_context', 'CONF-CTX'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    doi_url: str = generate_doi_external_url(
        protocol=settings.get('doi_proto', 'https'),
        domain=settings.get('doi_domain', 'doi.org'),
        context=settings.get('doi_context', 'CONF-CTX'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    ) if config.generate_external_doi_url else generate_doi_internal_url(
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    doi_path: str = generate_doi_path(
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    doi_identifier: str = generate_doi_identifier(
        context=settings.get('doi_context', '10.18429'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    doi_name: str = generate_doi_name(
        context=settings.get('doi_context', '10.18429'),
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    doi_landing_page = generate_doi_landing_page_url(
        organization=settings.get('doi_organization', 'JACoW'),
        conference=settings.get('doi_conference', 'CONF-YY'),
        contribution=contribution.code
    )

    event_isbn: str = settings.get('isbn', 'CONF-ISBN')
    event_issn: str = settings.get('issn', 'CONF-ISSN')

    primary_authors = [AuthorDOI(
        id=author.id,
        first_name=author.first,
        last_name=author.last,
        affiliation=author.affiliation
    ) for author in contribution.authors]

    track = None
    subtrack = None
    if contribution.track:
        if contribution.track.track_group:
            track = f'{contribution.track.track_group.code} - {contribution.track.track_group.title}'
            subtrack = f'{contribution.track.code} - {contribution.track.title}'
        else:
            track = f'{contribution.track.code} - {contribution.track.title}'

    doi_data = ContributionDOI(
        code=contribution.code,
        title=contribution.title,
        primary_authors=primary_authors,
        authors_groups=contribution.authors_groups,
        abstract=contribution.description,
        paper_url=contribution.url,
        slides_url=contribution.url,
        reference=contribution.reference,
        conference_code=event.title,
        venue=event.location,
        start_date=format_datetime_full(event.start),
        end_date=format_datetime_full(event.end),
        date=format_datetime_range_doi(event.start, event.end),
        editors=[
            EditorDOI(first_name=editor.first, last_name=editor.last,
                      affiliation=editor.affiliation)
            for editor in contribution.editors
        ],
        isbn=event_isbn,
        issn=event_issn,

        reception_date=format_datetime_doi(
            contribution.reception) if contribution.reception else '',
        revisitation_date=format_datetime_doi(
            contribution.revisitation) if contribution.revisitation else '',
        acceptance_date=format_datetime_doi(
            contribution.acceptance) if contribution.acceptance else '',
        issuance_date=format_datetime_doi(
            contribution.issuance) if contribution.issuance else '',

        reception_date_iso=format_datetime_doi_iso(
            contribution.reception) if contribution.reception else '',
        revisitation_date_iso=format_datetime_doi_iso(
            contribution.revisitation) if contribution.revisitation else '',
        acceptance_date_iso=format_datetime_doi_iso(
            contribution.acceptance) if contribution.acceptance else '',
        issuance_date_iso=format_datetime_doi_iso(
            contribution.issuance) if contribution.issuance else '',

        doi_label=doi_label,
        doi_url=doi_url,
        doi_path=doi_path,
        doi_identifier=doi_identifier,
        doi_name=doi_name,
        doi_landing_page=doi_landing_page,
        pages=f'{contribution.page}-{contribution.metadata.get("page_count", 0) + contribution.page - 1}'
        if contribution.page and contribution.metadata else '',
        num_of_pages=contribution.metadata.get(
            "page_count", 0) if contribution.metadata else 0,
        paper_size=contribution.paper_size,
        track=track if track else '',
        subtrack=subtrack if subtrack else ''

    )

    return doi_data


def refill_contribution_doi(proceedings_data: ProceedingsData, results: dict, callable: Callable) -> ProceedingsData:

    start_page: int = 0

    for contribution_data in proceedings_data.contributions:

        if callable(contribution_data):
            code: str = contribution_data.code

            if code in results and results[code] is not None:
                contribution_data.doi_data = results[code]
                contribution_data.doi_data.start_page = start_page
                start_page = start_page + contribution_data.doi_data.num_of_pages

    return proceedings_data
