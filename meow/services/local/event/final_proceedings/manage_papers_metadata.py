import logging as lg
from typing import Any

from fitz import Document
from fitz.utils import set_metadata

from nltk.stem.snowball import SnowballStemmer

from anyio import Path, create_task_group, CapacityLimiter, to_process, to_thread
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree
from meow.services.local.papers_metadata.pdf_report import get_pdf_report

from datetime import datetime
from meow.utils.datetime import format_datetime_pdf

from meow.utils.keywords import KEYWORDS


logger = lg.getLogger(__name__)


async def manage_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data)

    total_files: int = len(papers_data)
    processed_files: int = 0

    logger.info(f'manage_papers_metadata - files: {total_files}')

    if total_files == 0:
        raise Exception('no files found')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    stemmer = SnowballStemmer("english")
    stem_keywords_dict = stem_keywords_as_tree(KEYWORDS, stemmer)

    current_dt: datetime = datetime.now()
    current_dt_pdf: str = format_datetime_pdf(current_dt)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(6)

    results = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(manage_metadata_task, capacity_limiter, total_files,
                              current_index, current_paper, cookies, file_cache_dir,
                              stemmer, stem_keywords_dict, current_dt_pdf,
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

    proceedings_data = refill_contribution_metadata(proceedings_data, results)

    return proceedings_data


async def manage_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                               current_paper: ContributionPaperData, cookies: dict, pdf_cache_dir: Path,
                               stemmer, stem_keywords_dict, current_dt_pdf, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        contribution = current_paper.contribution
        current_file = current_paper.paper

        pdf_name = current_file.filename
        pdf_file = Path(pdf_cache_dir, pdf_name)
        pdf_path = str(await pdf_file.absolute())

        # logger.debug(f"{pdf_file} {pdf_name}")

        metadata = await to_process.run_sync(manage_metadata, contribution, pdf_path, stemmer, stem_keywords_dict, current_dt_pdf)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": metadata
        })


def manage_metadata(contribution: ContributionData, path: str, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]], current_dt_pdf) -> dict:
    """ """

    doc: Document | None

    try:
        doc = Document(filename=path)

        try:
            report = get_pdf_report(doc)
            keywords = get_keywords_from_text(doc, stemmer, stem_keywords_dict)

            metadata = dict(
                author=contribution.author_meta,
                producer=contribution.producer_meta,
                creator=contribution.creator_meta,
                title=contribution.title_meta,
                format=None,
                encryption=None,
                creationDate=current_dt_pdf,
                modDate=current_dt_pdf,
                subject=contribution.track_meta,
                keywords=", ".join(keywords),
                trapped=None,
            )

            set_metadata(doc, metadata)

            doc.saveIncr()

            return dict(
                keywords=keywords,
                report=report
            )
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
