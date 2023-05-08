import logging as lg
from typing import Callable

from nltk import download
from nltk.stem.snowball import SnowballStemmer

from anyio import Path, create_task_group, CapacityLimiter, to_thread
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_contributions_papers

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import pdf_to_text, read_report
from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree


from meow.utils.keywords import KEYWORDS


logger = lg.getLogger(__name__)


async def read_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - read_papers_metadata')

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(proceedings_data, callback)

    total_files: int = len(papers_data)
    processed_files: int = 0

    logger.info(f'read_papers_metadata - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)
    
    download('punkt')
    download('stopwords')

    stemmer = SnowballStemmer("english")
    stem_keywords_dict = stem_keywords_as_tree(KEYWORDS, stemmer)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(8)

    results = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_paper in enumerate(papers_data):
                tg.start_soon(read_metadata_task, capacity_limiter, total_files,
                              current_index, current_paper, cookies, file_cache_dir,
                              stemmer, stem_keywords_dict,
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


async def read_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                             current_paper: ContributionPaperData, cookies: dict, pdf_cache_dir: Path,
                             stemmer, stem_keywords_dict, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        current_file = current_paper.paper
        pdf_name = current_file.filename

        pdf_path = str(Path(pdf_cache_dir, pdf_name))

        # logger.debug(f"{pdf_file} {pdf_name}")

        [report, text] = await read_metadata_internal(pdf_path)

        keywords = await to_thread.run_sync(get_keywords_from_text, text, stemmer, stem_keywords_dict)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": dict(
                keywords=keywords,
                report=report
            )
        })


async def read_metadata_internal(path: str) -> list:

    result = dict(report=None, text=None)

    async def _report_task(p, r):
        r['report'] = await read_report(p)

    async def _text_task(p, r):
        r['text'] = await pdf_to_text(p)

    async with create_task_group() as tg:
        tg.start_soon(_report_task, path, result)
        tg.start_soon(_text_task, path, result)

    return [result.get('report'), result.get('text')]


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
