import logging as lg
from typing import Callable

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import read_report_anyio


logger = lg.getLogger(__name__)


async def read_papers_report(proceedings_data: ProceedingsData, cookies: dict,
                             settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - read_papers_report')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)
    processed_files: int = 0

    logger.info(f'read_papers_report - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    results = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(read_report_task, capacity_limiter, total_files,
                              current_index, current_paper, file_cache_dir,
                              send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:
                    processed_files = processed_files + 1

                    # logger.info(result)

                    file_data: FileData = result.get('file', None)

                    if file_data is not None:
                        results[file_data.uuid] = result.get('meta', None)

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    proceedings_data = refill_contribution_report(proceedings_data, results)

    return proceedings_data


async def read_report_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                           current_paper: ContributionPaperData, pdf_cache_dir: Path,
                           res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        current_file = current_paper.paper
        pdf_name = current_file.filename

        pdf_path = str(Path(pdf_cache_dir, pdf_name))

        # logger.debug(f"{pdf_file} {pdf_name}")

        report = await read_report_anyio(pdf_path, False)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": dict(
                report=report
            )
        })


def refill_contribution_report(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:

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

                    contribution_data.page = current_page
                    contribution_data.metadata = report

                    if report and 'page_count' in report:
                        current_page += report.get('page_count', 0)

                # logger.info('contribution_data pages = %s - %s', contribution_data.page,
                #   contribution_data.page + result.get('report').get('page_count'))

        except IndexError as e:
            logger.warning(f'No report for contribution {code}')
            logger.error(e, exc_info=True)
        except Exception as e:
            logger.error(e, exc_info=True)

    return proceedings_data
