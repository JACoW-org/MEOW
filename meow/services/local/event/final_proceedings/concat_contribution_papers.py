import logging as lg


import pathlib

from fitz import Document

from anyio import Path, create_task_group, CapacityLimiter, to_process
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    files_data: list[FileData] = await extract_proceedings_files(proceedings_data)

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    full_name = f"{proceedings_data.event.id}_full.pdf"
    full_pdf: Path = Path(file_cache_dir, full_name)

    pdf_files: list[str] = [
        str(await Path(file_cache_dir, c.filename).absolute())
        for c in files_data if c is not None
    ]

    await to_process.run_sync(concat_all, pdf_files, str(await full_pdf.absolute()))

    return proceedings_data


def concat_all(pdf_files: list[str], full_pdf: str):

    try:

        full_doc = Document()

        for pdf_file in pdf_files:
            curr_doc = Document(filename=pdf_file)
            full_doc.insert_pdf(curr_doc)

        full_doc.save(filename=full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)
