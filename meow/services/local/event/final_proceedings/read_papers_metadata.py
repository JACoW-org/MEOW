import logging as lg
from typing import Callable

from nltk import download

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import read_report_anyio


logger = lg.getLogger(__name__)


async def read_papers_metadata(proceedings_data: ProceedingsData, cookies: dict,
                               settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - read_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)
    processed_files: int = 0

    logger.info(f'read_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    download('punkt')
    download('stopwords')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(32)

    results = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(read_metadata_task, capacity_limiter, total_files,
                              current_index, current_paper, cookies, file_cache_dir,
                              send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:

                    processed_files = processed_files + 1

                    # logger.info(result)

                    file_data: FileData = result.get('file', None)

                    if file_data is not None:
                        results[file_data.uuid] = result.get('report', None)

                        if not results[file_data.uuid]:
                            raise BaseException('Error reading papers metadata')

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except BaseException as be:
            logger.error(be, exc_info=True)
            raise BaseException('Error reading papers metadata')

    proceedings_data = await refill_contribution_metadata(proceedings_data, results, file_cache_dir)

    return proceedings_data


async def read_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                             current_paper: ContributionPaperData, cookies: dict, pdf_cache_dir: Path,
                             stream: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        current_file = None

        try:

            current_file = current_paper.paper
            pdf_name = current_file.filename

            pdf_path = str(Path(pdf_cache_dir, pdf_name))

            # logger.debug(f"{pdf_file} {pdf_name}")

            report = await read_report_anyio(pdf_path, True)

            return await stream.send({
                "index": current_index,
                "total": total_files,
                "file": current_file,
                "report": report
            })

        except BaseException as be:
            logger.error(be, exc_info=True)

        return await stream.send(None)


async def refill_contribution_metadata(proceedings_data: ProceedingsData,
                                       results: dict, pdf_cache_dir: Path) -> ProceedingsData:

    current_page = 1

    for contribution_data in proceedings_data.contributions:
        code: str = ''

        try:

            if contribution_data and contribution_data.is_included_in_proceedings:

                code = contribution_data.code

                if contribution_data.paper and contribution_data.paper.latest_revision:

                    revision_data = contribution_data.paper.latest_revision

                    file_data = revision_data.files[-1] \
                        if len(revision_data.files) > 0 \
                        else None

                    if file_data is not None:

                        pdf_path = Path(pdf_cache_dir, file_data.filename)

                        if await pdf_path.exists():
                            contribution_data.paper_size = (await pdf_path.stat()).st_size

                        contribution_data.page = current_page

                        report: dict | None = results.get(file_data.uuid, None)

                        if report:
                            contribution_data.keywords = [
                                event_keyword_factory(keyword)
                                for keyword in report.get('keywords', [])
                            ]

                            contribution_data.metadata = report

                            if 'page_count' in report:
                                current_page += report.get('page_count', 0)

                    else:
                        logger.error(f"SKIPPED - no file_data: {code}")

                else:
                    logger.error(f"SKIPPED: {code}")

                    # logger.info('contribution_data pages = %s - %s', contribution_data.page,
                    # contribution_data.page + result.get('report').get('page_count'))

        except IndexError as e:
            logger.warning(f'No keyword for contribution {code}')
            logger.error(e, exc_info=True)
        except BaseException as be:
            logger.error(be, exc_info=True)

    return proceedings_data
