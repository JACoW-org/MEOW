import logging as lg

from fitz import Document

from anyio import Path, create_task_group, CapacityLimiter, to_process
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream

from anyio.streams.memory import MemoryObjectSendStream
from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_factory import event_keyword_factory
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree
from meow.services.local.papers_metadata.pdf_report import get_pdf_report

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
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

    full_name = f"{proceedings_data.event.id}_full.pdf"
    full_pdf: Path = Path(file_cache_dir, full_name)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(1)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files_data):
                tg.start_soon(concat_pdf_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, file_cache_dir,
                              full_pdf, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:
                    processed_files = processed_files + 1
                    
                    print(result)

                    if processed_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    return proceedings_data


async def concat_pdf_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int,
                          current_file: FileData, cookies: dict, pdf_cache_dir: Path, full_pdf: Path,
                          res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        pdf_name = current_file.filename
        pdf_file = Path(pdf_cache_dir, pdf_name)

        pdf_file_path = str(await pdf_file.absolute())
        full_pdf_path = str(await full_pdf.absolute())

        logger.info(f"{pdf_file} {pdf_name}")

        value = await to_process.run_sync(concat_pdf, pdf_file_path, full_pdf_path)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "value": value
        })


def concat_pdf(curr_pdf: str, full_pdf: str) -> dict | None:
    """ """

    # with open(path, 'rb') as fh:

    import pathlib

    pre_page_count = 0
    post_page_count = 0

    curr_doc: Document | None = None
    full_doc: Document | None = None

    try:

        if pathlib.Path(curr_pdf).is_file():
            curr_doc = Document(filename=curr_pdf)

        if pathlib.Path(full_pdf).is_file():
            pathlib.Path(full_pdf).rename(f"{full_pdf}.tmp")
            full_doc = Document(filename=f"{full_pdf}.tmp")
        else:
            full_doc = Document()

        if curr_doc is None:
            logger.info("No curr_doc")
            return None

        pre_page_count = full_doc.page_count

        full_doc.insert_pdf(curr_doc)

        post_page_count = full_doc.page_count

        full_doc.save(filename=full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)

    return dict(
        pre_page_count=pre_page_count,
        post_page_count=post_page_count
    )

    try:
        # pdf = Document(stream=fh.read(), filetype='pdf')

        full_doc = Document()
        full_doc.save(filename=full_pdf)

        curr_doc = Document(filename=curr_pdf)

        full_doc = Document(filename=full_pdf)

        pre_page_count = full_doc.page_count

        full_doc.insert_pdf(curr_doc)

        full_doc.write()

        post_page_count = full_doc.page_count

        logger.info(f"page_count: {pre_page_count} {post_page_count}")

        return dict(
            pre_page_count=pre_page_count,
            post_page_count=post_page_count
        )

    except Exception as e:
        logger.error(e, exc_info=True)
        raise e
