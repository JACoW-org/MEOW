import logging as lg

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.contribution_model import FileData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files


logger = lg.getLogger(__name__)


async def copy_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    files_data: list[FileData] = await extract_proceedings_files(proceedings_data)

    total_files: int = len(files_data)
    elaborated_files: int = 0

    # logger.debug(f'copy_contribution_papers - files: {total_files}')

    if total_files == 0:
        raise Exception('no file extracted')

    file_cache_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', file_cache_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f'{file_cache_dir} created!')
    
    pdf_dest_name = f"{proceedings_data.event.id}_hugo_src"
    pdf_dest_dir: Path = Path('var', 'run', pdf_dest_name, 'static', 'pdf')
    await pdf_dest_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f'{pdf_dest_dir} created!')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(6)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files_data):
                tg.start_soon(file_copy_task, capacity_limiter, total_files,
                              current_index, current_file, cookies, 
                              file_cache_dir, pdf_dest_dir, 
                              send_stream.clone())

        try:
            async with receive_stream:
                async for _ in receive_stream:
                    elaborated_files = elaborated_files + 1

                    if elaborated_files >= total_files:
                        receive_stream.close()

        except ClosedResourceError as e:
            logger.error(e)

    return proceedings_data


async def file_copy_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: FileData, 
                         cookies: dict, pdf_cache_dir: Path, pdf_dest_dir: Path, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        pdf_name = current_file.filename

        pdf_file = Path(pdf_cache_dir, pdf_name)
        pdf_dest = Path(pdf_dest_dir, pdf_name)

        pdf_exists = await pdf_file.exists()
        
        # logger.info(f"{pdf_file} ({'exists!' if pdf_exists else 'not exists!!!'}) -> {pdf_dest}")

        if pdf_exists:
            await pdf_dest.hardlink_to(pdf_file)
        else:
            logger.warning(f"{pdf_file} not exists")

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "exists": pdf_exists
        })
