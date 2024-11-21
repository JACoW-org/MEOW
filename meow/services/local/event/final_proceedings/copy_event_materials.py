import logging as lg

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.event_model import MaterialData
from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData)
from meow.utils.filesystem import move


logger = lg.getLogger(__name__)


async def copy_event_materials(proceedings_data: ProceedingsData,
                               cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    files_data: list[MaterialData] = [
        i for i in proceedings_data.materials
        if i.section not in ['final-proceedings-cover', 'at-a-glance-cover']
    ]

    total_files: int = len(files_data)
    elaborated_files: int = 0

    file_cache_name = f"{proceedings_data.event.id}_tmp"
    file_cache_dir: Path = Path("var", "run", file_cache_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    logger.info(f"{file_cache_dir} created!")

    pdf_dest_name = f"{proceedings_data.event.id}_src"
    pdf_dest_dir: Path = Path("var", "run", pdf_dest_name, "static", "pdf")
    await pdf_dest_dir.mkdir(exist_ok=True, parents=True)

    logger.info(f"{pdf_dest_dir} created!")

    vol_pdf_name = f"{proceedings_data.event.id}_proceedings_volume.pdf"
    vol_dest_name = f"{proceedings_data.event.path}_proceedings_volume.pdf"

    vol_pdf: Path = Path(file_cache_dir, vol_pdf_name)
    vol_dest: Path = Path(pdf_dest_dir, vol_dest_name)

    await vol_dest.unlink(missing_ok=True)

    if await vol_pdf.exists():
        # await vol_dest.hardlink_to(vol_pdf)
        await move(str(vol_pdf), str(vol_dest))

        await vol_dest.chmod(0o644)

    brief_pdf_name = f"{proceedings_data.event.id}_proceedings_brief.pdf"
    brief_dest_name = f"{proceedings_data.event.path}_proceedings_brief.pdf"

    brief_pdf: Path = Path(file_cache_dir, brief_pdf_name)
    brief_dest: Path = Path(pdf_dest_dir, brief_dest_name)

    await brief_dest.unlink(missing_ok=True)

    if await brief_pdf.exists():
        # await brief_dest.hardlink_to(brief_pdf)
        await move(str(brief_pdf), str(brief_dest))

        await brief_dest.chmod(0o644)

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files_data):
                tg.start_soon(
                    file_copy_task,
                    capacity_limiter,
                    total_files,
                    current_index,
                    current_file,
                    cookies,
                    file_cache_dir,
                    pdf_dest_dir,
                    send_stream.clone(),
                )

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
        except BaseException as ex:
            logger.error(ex, exc_info=True)
            raise ex

    return proceedings_data


async def file_copy_task(
    capacity_limiter: CapacityLimiter,
    total_files: int,
    current_index: int,
    current_file: MaterialData,
    cookies: dict,
    cache_dir: Path,
    dest_dir: Path,
    res: MemoryObjectSendStream,
) -> None:
    """ """

    async with capacity_limiter:
        file_exists = None

        try:
            file_name = f"{current_file.filename}"
            file_path = Path(cache_dir, file_name)

            dest_name = f"{current_file.filename}"
            dest_path = Path(dest_dir, dest_name)

            file_exists = await file_path.exists()

            await dest_path.unlink(missing_ok=True)

            # logger.info(f"{pdf_file} ({'exists!' if pdf_exists else 'not exists!!!'}) -> {pdf_dest}")

            if file_exists:
                # await dest_path.hardlink_to(file_path)
                await move(str(file_path), str(dest_path))

                await dest_path.chmod(0o644)
            else:
                logger.warning(f"{file_path} not exists")

        except Exception as ex:
            logger.error(ex, exc_info=True)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "exists": file_exists,
        })
