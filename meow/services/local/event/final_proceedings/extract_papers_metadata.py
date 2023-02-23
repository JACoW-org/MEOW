import logging as lg
from typing import Any

from fitz import Document

from nltk.stem.snowball import SnowballStemmer

from anyio import Path, create_task_group, CapacityLimiter, to_process
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree
from meow.services.local.papers_metadata.pdf_report import get_pdf_report
from meow.services.local.papers_metadata.pdf_to_txt import pdf_to_txt

from meow.utils.keywords import KEYWORDS


logger = lg.getLogger(__name__)


async def extract_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    files_data: list[FileData] = await extract_proceedings_files(proceedings_data)

    total_files: int = len(files_data)
    processed_files: int = 0

    # logger.debug(f'extract_papers_metadata - files: {total_files}')

    if total_files == 0:
        raise Exception('no files found')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    stemmer = SnowballStemmer("english")
    stem_keywords_dict = stem_keywords_as_tree(KEYWORDS, stemmer)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(4)
    
    results = dict()

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files_data):
                tg.start_soon(extract_metadata_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, file_cache_dir,
                              stemmer, stem_keywords_dict,
                              send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:
                    processed_files = processed_files + 1
                    
                    logger.info(result)
                    
                    file_data: FileData = result.get('file', None)
                    
                    if file_data is not None:
                        results[file_data.uuid] = result.get('meta', None)

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as e:
            logger.error(e)
    
    proceedings_data = refill_contribution_metadata(proceedings_data, results)        

    return proceedings_data


async def extract_metadata_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                                current_file: FileData, cookies: dict, pdf_cache_dir: Path,
                                stemmer, stem_keywords_dict, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        pdf_name = current_file.filename
        pdf_file = Path(pdf_cache_dir, pdf_name)

        logger.debug(f"{pdf_file} {pdf_name}")

        metadata = await to_process.run_sync(extract_metadata, str(await pdf_file.absolute()), stemmer, stem_keywords_dict)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "meta": metadata
        })


def extract_metadata(path: str, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]]) -> dict:
    """ """

    with open(path, 'rb') as fh:
        
        try:
            pdf = Document(stream=fh.read(), filetype='pdf')
            report = get_pdf_report(pdf)
            keywords = get_keywords_from_text(pdf, stemmer, stem_keywords_dict)

            return dict(
                keywords=keywords,
                report=report
            )

        except Exception as e:
            logger.error(e, exc_info=True)
            raise e


def refill_contribution_metadata(proceedings_data: ProceedingsData, results: dict) -> ProceedingsData:
    for contribution_data in proceedings_data.contributions:
        try:
            revision_data = contribution_data.revisions[-1]
            file_data = revision_data.files[-1]        
            contribution_data.metadata = results[file_data.uuid]
        except Exception:
            logger.info(f'No paper for contribution {contribution_data.code}')
            
    return proceedings_data