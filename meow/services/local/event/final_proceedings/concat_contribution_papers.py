import logging as lg

from math import sqrt

from anyio import CapacityLimiter, Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_model import AttachmentData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_papers
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import concat_pdf, write_metadata
from meow.utils.list import split_list


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name: str = f"{proceedings_data.event.id}_pdf"
    cache_dir: Path = Path('var', 'run', dir_name)
    await cache_dir.mkdir(exist_ok=True, parents=True)

    files_data = await extract_proceedings_papers(proceedings_data)

    async with create_task_group() as tg:
        tg.start_soon(vol_pdf_task, proceedings_data,
                      files_data, cache_dir)
        tg.start_soon(brief_pdf_task, proceedings_data,
                      files_data, cache_dir)

    return proceedings_data


async def vol_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title

    chunk_size = int(sqrt(len(files_data))) + 1

    vol_pre_pdf_path: Path | None = None

    try:
        
        attachments_data: list[AttachmentData] = proceedings_data.attachments
        for attachment_data in attachments_data:
            # {event_code}-{section_index}-{section_code}-{file_name}
            attachment_name: str = attachment_data.filename.split('.')[0]
            event_code, section_index, section_code, * \
                file_name = attachment_name.split('-')

            if section_code == 'volumes' and '-'.join(file_name) == 'proceedings-cover':
                vol_pre_pdf_path = Path(cache_dir, attachment_data.filename)
                
                if not await vol_pre_pdf_path.exists():
                    vol_pre_pdf_path = None

    except Exception as e:
        logger.error(e, exc_info=True)

    logger.warn("\n\n")
    logger.warn(str(vol_pre_pdf_path))
    logger.warn("\n\n")

    vol_pdf_path = Path(cache_dir, f"{event_id}_proceedings_volume.pdf")

    vol_pdf_files = [
        str(Path(cache_dir, f"{f.filename}_jacow"))
        for f in files_data
    ]

    vol_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(vol_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{vol_pdf_path}." + "{:010d}".format(index),
                          vol_pdf_files_chunk, vol_pdf_results, capacity_limiter)

    vol_pdf_results.sort()

    pdf_parts = [str(vol_pre_pdf_path)] + \
        vol_pdf_results if vol_pre_pdf_path else vol_pdf_results

    await concat_pdf(str(vol_pdf_path), pdf_parts)
    await metadata_vol(str(vol_pdf_path), event_title)

    proceedings_data.proceedings_volume_size = (await vol_pdf_path.stat()).st_size


async def brief_pdf_task(proceedings_data: ProceedingsData,  files_data: list[FileData], cache_dir: Path):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title
    
    brief_pre_pdf_path: Path | None = None
    
    try:

        attachments_data: list[AttachmentData] = proceedings_data.attachments
        for attachment_data in attachments_data:
            # {event_code}-{section_index}-{section_code}-{file_name}
            attachment_name: str = attachment_data.filename.split('.')[0]
            event_code, section_index, section_code, * \
                file_name = attachment_name.split('-')

            if section_code == 'volumes' and '-'.join(file_name) == 'at-a-glance-cover':
                brief_pre_pdf_path = Path(cache_dir, attachment_data.filename)
                
                if not await brief_pre_pdf_path.exists():
                    brief_pre_pdf_path = None

    except Exception as e:
        logger.error(e, exc_info=True)

    logger.warn("\n\n")
    logger.warn(str(brief_pre_pdf_path))
    logger.warn("\n\n")

    brief_pdf_path = Path(cache_dir, f"{event_id}_proceedings_brief.pdf")

    brief_pdf_files = [
        (str(Path(cache_dir, f"{f.filename}_jacow")) + ",,1")
        for f in files_data
    ]

    vol_pdf_results: list[str] = []

    chunk_size = int(sqrt(len(files_data))) + 1
    capacity_limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(brief_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{brief_pdf_path}." + "{:010d}".format(index),
                          vol_pdf_files_chunk, vol_pdf_results, capacity_limiter)

    brief_pdf_files.sort()
           
    pdf_parts = [str(brief_pre_pdf_path)] + \
        vol_pdf_results if brief_pre_pdf_path else vol_pdf_results

    await concat_pdf(str(brief_pdf_path), pdf_parts)
    await metadata_brief(str(brief_pdf_path), event_title)

    proceedings_data.proceedings_brief_size = (await brief_pdf_path.stat()).st_size


async def concat_chunks(write_path: str, pdf_files: list[str], results: list[str], limiter: CapacityLimiter) -> None:
    async with limiter:
        results.append(write_path)
        await concat_pdf(write_path, pdf_files)


async def metadata_vol(full_pdf: str, volume_title: str) -> None:
    """ """

    try:

        metadata = dict(
            author=f"JACoW - Joint Accelerator Conferences Website",
            producer=None,
            creator=f"cat--purr_meow",
            title=f"{volume_title} - Proceedings Volume",
            format=None,
            encryption=None,
            creationDate=None,
            modDate=None,
            subject=f"The complete volume of papers",
            keywords=None,
            trapped=None,
        )

        # logger.info(metadata)

        await write_metadata(metadata, full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)


async def metadata_brief(full_pdf: str, volume_title: str) -> None:
    """ """

    try:

        metadata = dict(
            author=f"JACoW - Joint Accelerator Conferences Website",
            producer=None,
            creator=f"cat--purr_meow",
            title=f"{volume_title} - Proceedings at a Glance",
            format=None,
            encryption=None,
            creationDate=None,
            modDate=None,
            subject=f"First page only of all papers with hyperlinks to complete versions",
            keywords=None,
            trapped=None,
        )

        # logger.info(metadata)

        await write_metadata(metadata, full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)
