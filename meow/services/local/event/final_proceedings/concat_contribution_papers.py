import logging as lg

from math import sqrt
from typing import Callable

from anyio import CapacityLimiter, Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_model import AttachmentData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_papers
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import brief_links, vol_toc, pdf_separate, pdf_unite, write_metadata
from meow.utils.list import split_list


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name: str = f"{proceedings_data.event.id}_tmp"
    cache_dir: Path = Path('var', 'run', dir_name)
    await cache_dir.mkdir(exist_ok=True, parents=True)

    files_data = await extract_proceedings_papers(proceedings_data, callback)

    if len(files_data) > 0:

        # await first_pdf_task(proceedings_data, files_data, cache_dir)
        await brief_pdf_task(proceedings_data, files_data, cache_dir)
        await vol_pdf_task(proceedings_data, files_data, cache_dir)

    return proceedings_data


async def first_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path):

    async def _task(current_file: FileData, capacity_limiter: CapacityLimiter):
        async with capacity_limiter:
            jacow_pdf_file = Path(cache_dir, f"{current_file.filename}_jacow")
            first_pdf_file = Path(cache_dir, f"{current_file.filename}_first")

            if await first_pdf_file.exists():
                await first_pdf_file.unlink()

            tg.start_soon(pdf_separate, str(jacow_pdf_file),
                          str(first_pdf_file), 1, 1)

    capacity_limiter = CapacityLimiter(8)
    async with create_task_group() as tg:
        for current_file in files_data:
            tg.start_soon(_task, current_file, capacity_limiter)


async def vol_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title

    chunk_size = int(sqrt(len(files_data))) + 1

    vol_pdf_path = Path(cache_dir, f"{event_id}_proceedings_volume.pdf")

    vol_pre_pdf_path = await get_vol_pre_pdf_path(proceedings_data, cache_dir)
    vol_toc_pdf_path = await get_vol_toc_pdf_path(proceedings_data, cache_dir)

    vol_pdf_files = [
        str(Path(cache_dir, f"{f.filename}_jacow"))
        for f in files_data
    ]

    vol_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(vol_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{vol_pdf_path}." + "{:010d}".format(index),
                          vol_pdf_files_chunk, vol_pdf_results, False, capacity_limiter)

    vol_pdf_results.sort()

    pdf_parts = [str(vol_pre_pdf_path)] + \
        vol_pdf_results if vol_pre_pdf_path else vol_pdf_results

    metadata = dict(
        author=f"JACoW - Joint Accelerator Conferences Website",
        producer=None,
        creator=f"cat--purr_meow",
        title=f"{event_title} - Proceedings Volume",
        format=None,
        encryption=None,
        creationDate=None,
        modDate=None,
        subject=f"The complete volume of papers",
        keywords=None,
        trapped=None,
    )

    await pdf_unite(str(vol_pdf_path), pdf_parts, False)
    await write_metadata(metadata, str(vol_pdf_path))

    proceedings_data.proceedings_volume_size = (await vol_pdf_path.stat()).st_size


async def get_vol_pre_pdf_path(proceedings_data: ProceedingsData, cache_dir: Path):
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

    return vol_pre_pdf_path


async def get_vol_toc_pdf_path(proceedings_data: ProceedingsData, cache_dir: Path):

    vol_toc_pdf_path: Path | None = None

    try:
        vol_toc_pdf_path = Path(
            cache_dir, f'{proceedings_data.event.id}_proceedings_toc.pdf')

        toc_data = [
            {
                "name":           "Five-storied Pagoda",
                "temple":         "Rurikō-ji",
                "founded":        "middle Muromachi period, 1442",
                "region":         "Yamaguchi, Yamaguchi",
                "position":       "34.190181,131.472917"
            },
            {
                "name":           "Founder's Hall",
                "temple":         "Eihō-ji",
                "founded":        "early Muromachi period",
                "region":         "Tajimi, Gifu",
                "position":       "35.346144,137.129189"
            },
            {
                "name":           "Fudōdō",
                "temple":         "Kongōbu-ji",
                "founded":        "early Kamakura period",
                "region":         "Kōya, Wakayama",
                "position":       "34.213103,135.580397"
            },
            {
                "name":           "Goeidō",
                "temple":         "Nishi Honganji",
                "founded":        "Edo period, 1636",
                "region":         "Kyoto",
                "position":       "34.991394,135.751689"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Murō-ji",
                "founded":        "early Heian period",
                "region":         "Uda, Nara",
                "position":       "34.536586819357986,136.0395548452301"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Fudō-in",
                "founded":        "late Muromachi period, 1540",
                "region":         "Hiroshima",
                "position":       "34.427014,132.471117"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Ninna-ji",
                "founded":        "Momoyama period, 1613",
                "region":         "Kyoto",
                "position":       "35.031078,135.713811"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Mii-dera",
                "founded":        "Momoyama period, 1599",
                "region":         "Ōtsu, Shiga",
                "position":       "35.013403,135.852861"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Tōshōdai-ji",
                "founded":        "Nara period, 8th century",
                "region":         "Nara, Nara",
                "position":       "34.675619,135.784842"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Tō-ji",
                "founded":        "Momoyama period, 1603",
                "region":         "Kyoto",
                "position":       "34.980367,135.747686"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Tōdai-ji",
                "founded":        "middle Edo period, 1705",
                "region":         "Nara, Nara",
                "position":       "34.688992,135.839822"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Hōryū-ji",
                "founded":        "Asuka period, by 693",
                "region":         "Ikaruga, Nara",
                "position":       "34.614317,135.734458"
            },
            {
                "name":           "Golden Hall",
                "temple":         "Daigo-ji",
                "founded":        "late Heian period",
                "region":         "Kyoto",
                "position":       "34.951481,135.821747"
            },
            {
                "name":           "Keigū-in Main Hall",
                "temple":         "Kōryū-ji",
                "founded":        "early Kamakura period, before 1251",
                "region":         "Kyoto",
                "position":       "35.015028,135.705425"
            },
            {
                "name":           "Konpon-chūdō",
                "temple":         "Enryaku-ji",
                "founded":        "early Edo period, 1640",
                "region":         "Ōtsu, Shiga",
                "position":       "35.070456,135.840942"
            },
            {
                "name":           "Korō",
                "temple":         "Tōshōdai-ji",
                "founded":        "early Kamakura period, 1240",
                "region":         "Nara, Nara",
                "position":       "34.675847,135.785069"
            },
            {
                "name":           "Kōfūzō",
                "temple":         "Hōryū-ji",
                "founded":        "early Heian period",
                "region":         "Ikaruga, Nara",
                "position":       "34.614439,135.735428"
            },
            {
                "name":           "Large Lecture Hall",
                "temple":         "Hōryū-ji",
                "founded":        "middle Heian period, 990",
                "region":         "Ikaruga, Nara",
                "position":       "34.614783,135.734175"
            },
            {
                "name":           "Lecture Hall",
                "temple":         "Zuiryū-ji",
                "founded":        "early Edo period, 1655",
                "region":         "Takaoka, Toyama",
                "position":       "36.735689,137.010019"
            },
            {
                "name":           "Lecture Hall",
                "temple":         "Tōshōdai-ji",
                "founded":        "Nara period, 763",
                "region":         "Nara, Nara",
                "position":       "34.675933,135.784842"
            },
            {
                "name":           "Lotus Flower Gate",
                "temple":         "Tō-ji",
                "founded":        "early Kamakura period",
                "region":         "Kyoto",
                "position":       "34.980678,135.746314"
            },
            {
                "name":           "Main Hall",
                "temple":         "Akishinodera",
                "founded":        "early Kamakura period",
                "region":         "Nara, Nara",
                "position":       "34.703769,135.776189"
            }
        ]

        await vol_toc(str(vol_toc_pdf_path), toc_data)

    except Exception as e:
        logger.error(e, exc_info=True)

    return vol_toc_pdf_path


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

    brief_pdf_path = Path(cache_dir, f"{event_id}_proceedings_brief.pdf")

    brief_pdf_files = [
        (str(Path(cache_dir, f"{f.filename}_jacow")))
        for f in files_data
    ]

    brief_pdf_links = [
        f.filename for f in files_data
    ]

    vol_pdf_results: list[str] = []

    chunk_size = int(sqrt(len(files_data))) + 1
    capacity_limiter = CapacityLimiter(4)

    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(brief_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{brief_pdf_path}." + "{:010d}".format(index),
                          vol_pdf_files_chunk, vol_pdf_results, True, capacity_limiter)

    brief_pdf_files.sort()

    pdf_parts = [str(brief_pre_pdf_path)] + \
        vol_pdf_results if brief_pre_pdf_path else vol_pdf_results

    metadata = dict(
        author=f"JACoW - Joint Accelerator Conferences Website",
        producer=None,
        creator=f"cat--purr_meow",
        title=f"{event_title} - Proceedings at a Glance",
        format=None,
        encryption=None,
        creationDate=None,
        modDate=None,
        subject=f"First page only of all papers with hyperlinks to complete versions",
        keywords=None,
        trapped=None,
    )

    await pdf_unite(str(brief_pdf_path), pdf_parts)
    await write_metadata(metadata, str(brief_pdf_path))
    await brief_links(str(brief_pdf_path), brief_pdf_links)

    proceedings_data.proceedings_brief_size = (await brief_pdf_path.stat()).st_size


async def concat_chunks(write_path: str, pdf_files: list[str], results: list[str], first: bool, limiter: CapacityLimiter) -> None:
    async with limiter:
        results.append(write_path)
        await pdf_unite(write_path, pdf_files, first)
        # await concat_pdf(write_path, pdf_files, None)
