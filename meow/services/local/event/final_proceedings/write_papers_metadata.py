import logging as lg
from typing import Any, Callable, Optional
import pytz as tz

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from rdflib import URIRef
from rdflib.term import Literal
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionPaperData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.event_pdf_utils import draw_frame_anyio

from datetime import datetime
from meow.utils.datetime import format_datetime_pdf
from meow.utils.filesystem import copy
from meow.utils.xmp import DC, PDF, XMP, XMPMetadata


logger = lg.getLogger(__name__)


async def write_papers_metadata(proceedings_data: ProceedingsData, cookies: dict,
                                settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - write_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)
    processed_files: int = 0

    # logger.info(f'write_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(64)

    timezone = tz.timezone(settings.get('timezone', 'UTC'))
    current_dt: datetime = datetime.now(tz=timezone)
    current_dt_pdf: str = format_datetime_pdf(current_dt)

    sessions_dict: dict[str, SessionData] = dict()

    for session in proceedings_data.sessions:
        sessions_dict[session.code] = session

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(write_metadata_task, capacity_limiter,
                              total_files, current_index, current_paper,
                              sessions_dict, current_dt_pdf, settings,
                              file_cache_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:

                    if not result:
                        raise BaseException('Error writing papers metadata')

                    processed_files = processed_files + 1

                    # logger.info(result)

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except BaseException as be:
            logger.error(be, exc_info=True)
            raise BaseException('Error writing papers metadata')

    return proceedings_data


async def write_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                              current_paper: ContributionPaperData, sessions: dict[str, SessionData],
                              current_dt_pdf: datetime, settings: dict, pdf_cache_dir: Path,
                              stream: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        try:

            contribution = current_paper.contribution
            session = sessions.get(contribution.session_code)
            current_file = current_paper.paper

            original_pdf_name = f"{current_file.filename}"
            original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

            jacow_pdf_name = f"{current_file.filename}_jacow"
            jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

            if await jacow_pdf_file.exists():
                await jacow_pdf_file.unlink()

            # logger.debug(f"{pdf_file} {pdf_name}")

            # await copy(str(original_pdf_file), str(jacow_pdf_file))

            header_data: Optional[dict] = get_header_data(contribution)
            footer_data: Optional[dict] = get_footer_data(
                contribution, session)
            metadata: Optional[dict] = get_metadata(contribution)
            xml_metadata: Optional[str] = get_xml_metatdata(contribution)

            pre_print: str = settings.get('pre_print', 'This is a preprint') \
                if contribution.peer_reviewing_accepted else ''

            await draw_frame_anyio(str(original_pdf_file), str(jacow_pdf_file),
                                   contribution.page, pre_print, header_data,
                                   footer_data, metadata, xml_metadata)

            return await stream.send({
                "index": current_index,
                "total": total_files,
                "file": current_file
            })

        except BaseException as be:
            logger.error(be, exc_info=True)

        return await stream.send(None)


def get_metadata(contribution: ContributionData) -> dict[str, Any] | None:

    if not contribution.doi_data:
        return None

    metadata = dict(
        author=contribution.authors_meta,
        producer=contribution.producer_meta,
        creator=contribution.creator_meta,
        title=contribution.title_meta,
        format='application/pdf',
        encryption=None,
        creationDate=contribution.doi_data.reception_date,
        modDate=contribution.doi_data.acceptance_date,
        subject=contribution.track_meta,
        keywords=contribution.keywords_meta,
        trapped=None,
    )

    return metadata


def get_xml_metatdata(contribution: ContributionData) -> str | None:

    if not contribution.doi_data:
        return None

    meta = XMPMetadata(contribution.doi_data.doi_url)

    meta.set(DC.title, Literal(contribution.title_meta))
    meta.set(DC.subject, Literal(contribution.track_meta))
    meta.set(DC.description, Literal(contribution.doi_data.abstract))
    meta.set(DC.language, Literal("en-us"))
    meta.set(URIRef('http://purl.org/dc/terms/format'),
             Literal("application/pdf"))
    meta.set(DC.creator, Literal(contribution.authors_meta))
    meta.set(PDF.Keywords, Literal(contribution.keywords_meta))
    meta.set(PDF.Producer, Literal(contribution.producer_meta))
    meta.set(XMP.CreatorTool, Literal(contribution.creator_tool_meta))
    meta.set(XMP.Identifier, Literal(contribution.doi_data.doi_identifier))
    meta.set(XMP.ModifyDate, Literal(contribution.doi_data.acceptance_date))
    meta.set(XMP.MetadataDate, Literal(contribution.doi_data.acceptance_date))
    meta.set(XMP.CreateDate, Literal(contribution.doi_data.reception_date))

    return meta.to_xml()


def get_footer_data(contribution, session) -> dict[str, str] | None:

    classificationHeader = f'{contribution.track.title}' if contribution.track else ''
    sessionHeader = f'{session.code}: {session.title}' if session else ''

    footer_data = dict(
        classificationHeader=classificationHeader,
        sessionHeader=sessionHeader,
        contributionCode=contribution.code
    )

    return footer_data


def get_header_data(contribution: ContributionData) -> dict[str, str] | None:

    header_data = dict(
        series=contribution.doi_data.series,
        venue=f'{contribution.doi_data.conference_code},{contribution.doi_data.venue}',
        isbn=contribution.doi_data.isbn,
        issn=contribution.doi_data.issn,
        doi=contribution.doi_data.doi_name
    ) if contribution.doi_data else None

    return header_data


def refill_contribution_metadata(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:

    current_page = 1

    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code

        try:
            if contribution_data.paper and contribution_data.paper.latest_revision:
                revision_data = contribution_data.paper.latest_revision
                file_data = revision_data.files[-1] \
                    if len(revision_data.files) > 0 \
                    else None

                if file_data is not None:

                    result: dict = results.get(file_data.uuid, {})
                    report: dict = result.get('report', {})

                    contribution_data.keywords = [
                        event_keyword_factory(keyword)
                        for keyword in result.get('keywords', [])
                    ]

                    contribution_data.page = current_page
                    contribution_data.metadata = report

                    if report and 'page_count' in report:
                        current_page += report.get('page_count', 0)

                # logger.info('contribution_data pages = %s - %s', contribution_data.page, contribution_data.page
                #   + result.get('report').get('page_count'))

        except IndexError as e:
            logger.warning(f'No keyword for contribution {code}')
            logger.error(e, exc_info=True)
        except Exception as e:
            logger.error(e, exc_info=True)

    return proceedings_data
