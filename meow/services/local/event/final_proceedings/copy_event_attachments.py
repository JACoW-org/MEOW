import logging as lg

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.event_model import AttachmentData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def copy_event_attachments(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    files_data: list[AttachmentData] = proceedings_data.attachments

    total_files: int = len(files_data)
    elaborated_files: int = 0

    # logger.debug(f'copy_event_attachments - files: {total_files}')

    # if total_files == 0:
    #     raise Exception('no file extracted')

    file_cache_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', file_cache_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f'{file_cache_dir} created!')
    
    pdf_dest_name = f"{proceedings_data.event.id}_hugo_src"
    pdf_dest_dir: Path = Path('var', 'run', pdf_dest_name, 'static', 'pdf')
    await pdf_dest_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f'{pdf_dest_dir} created!')
    
    vol_name = f"{proceedings_data.event.id}_proceedings_volume.pdf"
    vol_pdf: Path = Path(file_cache_dir, vol_name)
    vol_dest: Path = Path(pdf_dest_dir, vol_name)
    
    if await vol_pdf.exists():
        await vol_dest.hardlink_to(vol_pdf)
    
    brief_name = f"{proceedings_data.event.id}_proceedings_brief.pdf"
    brief_pdf: Path = Path(file_cache_dir, brief_name)
    brief_dest: Path = Path(pdf_dest_dir, brief_name)
    
    if await brief_pdf.exists():
        await brief_dest.hardlink_to(brief_pdf)
    
    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(4)

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

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=True)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=True)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    return proceedings_data


async def file_copy_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: AttachmentData, 
                         cookies: dict, cache_dir: Path, dest_dir: Path, res: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:
        
        file_exists = None
        
        try:
               
            file_name = f"{current_file.filename}"
            file_path = Path(cache_dir, file_name)
            
            dest_name = f"{current_file.filename}"
            dest_path = Path(dest_dir, dest_name)
            
            dest_exists = await dest_path.exists()
            file_exists = await file_path.exists()
            
            if dest_exists:
                await dest_path.unlink()
            
            # logger.info(f"{pdf_file} ({'exists!' if pdf_exists else 'not exists!!!'}) -> {pdf_dest}")

            if file_exists:
                await dest_path.hardlink_to(file_path)
            else:
                logger.warning(f"{file_path} not exists")
            
        except Exception as ex:
            logger.error(ex, exc_info=True)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "exists": file_exists
        })
