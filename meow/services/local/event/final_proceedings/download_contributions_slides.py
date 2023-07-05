import logging as lg

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_slides

from meow.utils.http import download_file
from meow.services.local.event.event_pdf_utils import is_to_download
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def download_contributions_slides(proceedings_data: ProceedingsData, cookies: dict, settings: dict):
    """ """

    logger.info('event_final_proceedings - download_contributions_papers')

    files_data: list[FileData] = await extract_proceedings_slides(proceedings_data)

    total_files: int = len(files_data)
    downloaded_files: int = 0

    # logger.debug(f'download_contributions_papers - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_tmp"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files_data):
                tg.start_soon(file_download_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, file_cache_dir,
                              send_stream.clone())

        try:
            async with receive_stream:
                async for _ in receive_stream:
                    downloaded_files = downloaded_files + 1

                    # logger.info(
                    #     f"downloaded_files: {downloaded_files} - {total_files}")

                    if downloaded_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    return [proceedings_data, files_data]


async def file_download_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                             current_file: FileData, cookies: dict, pdf_cache_dir: Path,
                             res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        try:
            pdf_md5 = current_file.md5sum
            pdf_name = current_file.filename
            pdf_url = current_file.external_download_url

            http_sess = cookies.get('indico_session_http', '')
            https_sess = cookies.get('indico_session', '')

            indico_cookies = dict(indico_session_http=http_sess,
                                  indico_session=https_sess)

            pdf_file = Path(pdf_cache_dir, pdf_name)

            # logger.debug(f"{pdf_md5} {pdf_name}")

            if await is_to_download(pdf_file, pdf_md5):
                # logger.info(f"download_file --> {pdf_url}")
                await download_file(url=pdf_url, file=pdf_file,
                                    cookies=indico_cookies)
            # else:
            #     logger.info(f"cached_file --> {pdf_url}")

        except Exception as ex:
            logger.error(ex, exc_info=True)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file
        })
