import logging as lg

from typing import AsyncGenerator

from io import open
from fitz import Document

from anyio import Path, create_task_group, CapacityLimiter, to_process
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream

from meow.services.local.event.event_pdf_check import extract_event_pdf_files
from meow.services.local.event.event_pdf_utils import is_to_download

from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree
from meow.services.local.papers_metadata.pdf_to_txt import pdf_to_txt

from meow.utils.http import download_file

from nltk.stem.snowball import SnowballStemmer

from meow.utils import keywords


logger = lg.getLogger(__name__)


async def event_pdf_keywords(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    # logger.debug(f'event_pdf_download - count: {len(contributions)} - cookies: {cookies}')

    stemmer = SnowballStemmer("english")

    # stem default keywords
    stem_keywords_dict = stem_keywords_as_tree(keywords.KEYWORDS, stemmer)

    event_id = event.get('id', 'event')

    pdf_cache_dir: Path = Path('var', 'run', f"{event_id}_pdf")
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    files = await extract_event_pdf_files(event)

    total_files: int = len(files)
    checked_files: int = 0

    # logger.debug(f'event_pdf_check - files: {len(files)}')

    send_stream, receive_stream = create_memory_object_stream()

    capacity_limiter = CapacityLimiter(4)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files):
                tg.start_soon(pdf_keywords_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, pdf_cache_dir,
                              stemmer, stem_keywords_dict, send_stream.clone())

        try:
            async with receive_stream:
                async for report in receive_stream:
                    checked_files = checked_files + 1

                    # print('receive_reports_stream::report-->',
                    #       checked_files, total_files, report)

                    yield dict(
                        type='progress',
                        value=report
                    )

                    if checked_files >= total_files:
                        receive_stream.close()

                        yield dict(
                            type='final',
                            value=None
                        )

        except ClosedResourceError as e:
            logger.error(e)


async def pdf_keywords_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: dict, cookies: dict, pdf_cache_dir: Path, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]], res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        keywords = await internal_pdf_keywords_task(current_file, cookies, pdf_cache_dir, stemmer, stem_keywords_dict)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "keywords": keywords
        })


async def internal_pdf_keywords_task(current_file: dict, cookies: dict, pdf_cache_dir: Path, stemmer: SnowballStemmer,
                                     stem_keywords_dict: dict[str, list[str]]) -> list[str]:
    """ """

    pdf_md5 = current_file.get('md5sum', '')
    pdf_name = current_file.get('filename', '')
    http_sess = cookies.get('indico_session_http', '')
    pdf_url = current_file.get('external_download_url', '')

    pdf_file = Path(pdf_cache_dir, pdf_name)

    logger.debug(f"{pdf_md5} {pdf_name}")

    if await is_to_download(pdf_file, pdf_md5):
        cookies = dict(indico_session_http=http_sess)
        await download_file(url=pdf_url, file=pdf_file, cookies=cookies)

    # IN PROCESS
    # paper_keywords = get_keywords_from_text(str(await pdf_file.absolute()), stemmer, stem_keywords_dict)

    # EXTERNAL THREAD
    # paper_keywords = await to_thread.run_sync(get_keywords_from_pdf, str(await pdf_file.absolute()), stemmer, stem_keywords_dict)

    # EXTERNAL PROCESS
    paper_keywords = await to_process.run_sync(get_pdf_keywords, str(await pdf_file.absolute()), stemmer, stem_keywords_dict)

    return paper_keywords


def get_pdf_keywords(path: str, stemmer: SnowballStemmer, stem_keywords_dict: dict[str, list[str]]) -> list[str]:

    with open(path, 'rb') as fh:
               
        try:           
            pdf = Document(stream=fh.read(), filetype='pdf')
            keywords = get_keywords_from_text(pdf, stemmer, stem_keywords_dict)
            return keywords
            
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e