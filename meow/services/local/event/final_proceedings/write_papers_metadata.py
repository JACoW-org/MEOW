import logging as lg
from typing import Any

from fitz import Document
from fitz.utils import set_metadata

from anyio import Path, create_task_group, CapacityLimiter, to_process, to_thread
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def write_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data)

    total_files: int = len(papers_data)
    processed_files: int = 0

    logger.info(f'write_papers_metadata - files: {total_files}')

    if total_files == 0:
        raise Exception('no files found')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(6)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(write_metadata_task, capacity_limiter, total_files,
                              current_index, current_paper, cookies, file_cache_dir,
                              send_stream.clone())

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
                              current_paper: ContributionPaperData, cookies: dict, pdf_cache_dir: Path,
                              res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        contribution = current_paper.contribution
        current_file = current_paper.paper

        read_pdf_name = f"{current_file.filename}"
        read_pdf_file = Path(pdf_cache_dir, read_pdf_name)
        read_pdf_path = str(await read_pdf_file.absolute())

        write_pdf_name = f"{current_file.filename}_jacow"
        write_pdf_file = Path(pdf_cache_dir, write_pdf_name)
        write_pdf_path = str(await write_pdf_file.absolute())

        # logger.debug(f"{pdf_file} {pdf_name}")

        metadata = await to_process.run_sync(write_metadata, contribution, read_pdf_path, write_pdf_path)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": metadata
        })


def write_metadata(contribution: ContributionData, read_path: str, write_path: str) -> None:
    """ """

    doc: Document | None

    try:
        doc = Document(filename=read_path)

        try:
            metadata = dict(
                author=contribution.authors_meta,
                producer=contribution.producer_meta,
                creator=contribution.creator_meta,
                title=contribution.title_meta,
                format=None,
                encryption=None,
                creationDate="",
                modDate="",
                subject=contribution.track_meta,
                keywords=contribution.keywords_meta,
                trapped=None,
            )

            # logger.info(metadata)

            set_metadata(doc, metadata)

            doc.save(filename=write_path, garbage=1, clean=1,
                     deflate=1, deflate_fonts=1, deflate_images=1)

        except Exception as e:
            logger.error(e, exc_info=True)
            raise e
        finally:
            if doc is not None:
                doc.close()

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def refill_contribution_metadata(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:

    current_page = 1

    for contribution_data in proceedings_data.contributions:
        code: str = contribution_data.code

        try:
            if contribution_data.latest_revision:
                revision_data = contribution_data.latest_revision
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
