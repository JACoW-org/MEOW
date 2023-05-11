import logging as lg
from typing import Callable, Optional
import pytz as tz

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.event_pdf_utils import write_metadata, draw_frame

from datetime import datetime
from meow.utils.datetime import format_datetime_pdf


logger = lg.getLogger(__name__)


async def write_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - write_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)
    processed_files: int = 0

    # logger.info(f'write_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(8)

    timezone = tz.timezone(settings.get('timezone', 'UTC'))
    current_dt: datetime = datetime.now(tz=timezone)
    current_dt_pdf: str = format_datetime_pdf(current_dt)

    sessions_dict: dict[str, SessionData] = dict()

    for session in proceedings_data.sessions:
        sessions_dict[session.code] = session

    cc_logo_bytes = await Path('cc_by.png').read_bytes()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(write_metadata_task, capacity_limiter, total_files,
                              current_index, current_paper, sessions_dict,
                              current_dt_pdf, cc_logo_bytes, cookies,
                              file_cache_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for _ in receive_stream:
                    processed_files = processed_files + 1

                    # logger.info(result)

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    return proceedings_data


async def write_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                              current_paper: ContributionPaperData, sessions: dict[str, SessionData], current_dt_pdf: datetime, cc_logo: bytes,
                              cookies: dict, pdf_cache_dir: Path,
                              res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        contribution = current_paper.contribution
        session = sessions.get(contribution.session_code)
        current_file = current_paper.paper

        read_pdf_name = f"{current_file.filename}"
        read_pdf_file = Path(pdf_cache_dir, read_pdf_name)
        read_pdf_path = str(read_pdf_file)

        write_pdf_name = f"{current_file.filename}_jacow"
        write_pdf_file = Path(pdf_cache_dir, write_pdf_name)
        write_pdf_path = str(write_pdf_file)

        # logger.debug(f"{pdf_file} {pdf_name}")

        metadata = dict(
            author=contribution.authors_meta,
            producer=contribution.producer_meta,
            creator=contribution.creator_meta,
            title=contribution.title_meta,
            format=None,
            encryption=None,
            creationDate=current_dt_pdf,
            modDate=current_dt_pdf,
            subject=contribution.track_meta,
            keywords=contribution.keywords_meta,
            trapped=None,
        )

        await write_metadata(metadata, read_pdf_path, write_pdf_path)

        start_page: int = contribution.page
        header_data: Optional[dict] = get_header_data(contribution)
        footer_data: Optional[dict] = get_footer_data(contribution, session)

        await draw_frame(write_pdf_path, start_page, header_data, footer_data)

        # await to_thread.run_sync(draw_frame, contribution, session, write_pdf_path, cc_logo)

        # venv/bin/python3 meow.py metadata -input var/html/FEL2022/pdf/12_proceedings_brief.pdf -title mario -author minnie  -keywords pippo

        # metadata = await to_process.run_sync(write_metadata, contribution, session, current_dt_pdf, read_pdf_path, write_pdf_path)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": metadata
        })


def get_footer_data(contribution, session) -> dict[str, str] | None:

    classificationHeader = f'{contribution.track.code}: {contribution.track.title}' if contribution.track else ''
    sessionHeader = f'{session.code}: {session.title}' if session else ''

    footer_data = dict(
        classificationHeader=classificationHeader,
        sessionHeader=sessionHeader,
        contributionCode=contribution.code
    )

    return footer_data


def get_header_data(contribution) -> dict[str, str] | None:

    venue = f'{contribution.doi_data.conference_code},{contribution.doi_data.venue}'

    header_data = dict(
        series=contribution.doi_data.series,
        venue=venue,
        isbn=contribution.doi_data.isbn,
        issn=contribution.doi_data.issn,
        doi=contribution.doi_data.doi_url
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

                # logger.info('contribution_data pages = %s - %s', contribution_data.page, contribution_data.page + result.get('report').get('page_count'))

        except IndexError as e:
            logger.warning(f'No keyword for contribution {code}')
            logger.error(e, exc_info=True)
        except Exception as e:
            logger.error(e, exc_info=True)

    return proceedings_data
