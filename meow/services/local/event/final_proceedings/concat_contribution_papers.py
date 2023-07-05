import logging as lg

from math import sqrt
from typing import Callable

from anyio import CapacityLimiter, Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_model import AttachmentData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_papers
from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig, ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import brief_links, vol_toc, pdf_separate, pdf_unite, write_metadata
from meow.utils.list import split_list
from meow.utils.serialization import json_encode
from meow.models.local.event.final_proceedings.track_model import TrackGroupData


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict, config: FinalProceedingsConfig, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name: str = f"{proceedings_data.event.id}_tmp"
    cache_dir: Path = Path('var', 'run', dir_name)
    await cache_dir.mkdir(exist_ok=True, parents=True)

    files_data = await extract_proceedings_papers(proceedings_data, callback)

    if len(files_data) > 0:

        toc_grouping = settings.get('toc_grouping', [])

        # await first_pdf_task(proceedings_data, files_data, cache_dir)
        await brief_pdf_task(proceedings_data, files_data, cache_dir, settings.get('doi_conference', 'CONF-YY'), config.absolute_pdf_link)
        await vol_pdf_task(proceedings_data, files_data, cache_dir, callback, toc_grouping)

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


async def vol_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path, callback: Callable, toc_grouping: list[str]):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title

    chunk_size = int(sqrt(len(files_data))) + 1

    vol_pdf_path = Path(cache_dir, f"{event_id}_proceedings_volume.pdf")

    vol_pre_pdf_path = await get_vol_pre_pdf_path(proceedings_data, cache_dir, callback)
    vol_toc_pdf_path = await get_vol_toc_pdf_path(proceedings_data, vol_pre_pdf_path, cache_dir, callback, toc_grouping)

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

    pdf_parts = [str(vol_pre_pdf_path)] if vol_pre_pdf_path else []
    pdf_parts = pdf_parts + [str(vol_toc_pdf_path)] if vol_toc_pdf_path else []
    pdf_parts = pdf_parts + vol_pdf_results

    metadata = dict(
        author="JACoW - Joint Accelerator Conferences Website",
        producer=None,
        creator="cat--purr_meow",
        title=f"{event_title} - Proceedings Volume",
        format=None,
        encryption=None,
        creationDate=None,
        modDate=None,
        subject="The complete volume of papers",
        keywords=None,
        trapped=None,
    )

    await pdf_unite(str(vol_pdf_path), pdf_parts, False)
    await write_metadata(metadata, str(vol_pdf_path))

    proceedings_data.proceedings_volume_size = (await vol_pdf_path.stat()).st_size


async def get_vol_pre_pdf_path(proceedings_data: ProceedingsData, cache_dir: Path, callback: Callable):
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


async def get_vol_toc_pdf_path(proceedings_data: ProceedingsData, vol_pre_pdf_path: Path | None, cache_dir: Path, callback: Callable, toc_grouping: list[str]):

    vol_toc_pdf_path: Path | None = None
    vol_toc_conf_path: Path | None = None

    logger.info(toc_grouping)

    try:
        vol_toc_name = f'{proceedings_data.event.id}_proceedings_toc'

        vol_toc_pdf_path = Path(cache_dir, f"{vol_toc_name}.pdf")
        vol_toc_conf_path = Path(cache_dir, f"{vol_toc_name}.json")

        track_groups = dict()

        logger.info(
            f'get_vol_toc_pdf_path - number of contributions: {len(proceedings_data.contributions)}')

        for contribution in proceedings_data.contributions:

            if callback(contribution) is False or contribution.track is None:
                continue

            track_group = contribution.track.track_group or TrackGroupData(
                code='default', title='Default', description='description', position=0)
            if track_group.code not in track_groups:
                track_groups[track_group.code] = dict(
                    title=track_group.title,
                    page=contribution.page,
                    tracks=dict()
                )

            track = contribution.track

            if track.code not in track_groups[track_group.code]['tracks']:
                track_groups[track_group.code]['tracks'][track.code] = dict(
                    title=track.title,
                    page=contribution.page,
                    contributions=dict()
                )
            track_groups[track_group.code]['tracks'][track.code]['contributions'][contribution.code] = dict(
                title=contribution.title,
                page=contribution.page
            )

        toc_items = list()
        toc_settings = dict(
            include_track_group='track_group' in toc_grouping,
            include_tracks='track' in toc_grouping,
            include_contributions='contribution' in toc_grouping
        )

        for group_code, track_group in track_groups.items():
            if toc_settings.get('include_track_group'):
                toc_items.append({'type': 'track_group', 'code': group_code, 'title': track_group.get(
                    'title'), 'page': track_group.get('page')})

            for track_code, track in track_group.get('tracks').items():
                if toc_settings.get('include_tracks'):
                    toc_items.append({'type': 'track', 'code': track_code, 'title': track.get(
                        'title'), 'page': track.get('page')})

                if toc_settings.get('include_contributions'):
                    for contrib_code, contrib_data in track.get('contributions').items():
                        toc_items.append({'type': 'contribution', 'code': contrib_code, 'title': contrib_data.get(
                            'title'), 'page': contrib_data.get('page')})

        toc_data: dict = {
            "toc_title": "Table of Contents",
            "pre_pdf": str(vol_pre_pdf_path) if vol_pre_pdf_path else None,
            "vol_file": f"{proceedings_data.event.id}_proceedings_volume.pdf",
            "toc_items": toc_items,
            "toc_settings": toc_settings,
            "event": dict(
                name=proceedings_data.event.name,
                title=proceedings_data.event.title,
                series=proceedings_data.event.series,
                isbn=proceedings_data.event.isbn,
                doi=proceedings_data.event.doi_label,
                issn=proceedings_data.event.issn,
            )
        }

        await vol_toc_conf_path.write_text(json_encode(toc_data).decode('utf-8'))

        await vol_toc(str(vol_toc_pdf_path), str(vol_toc_conf_path))

    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        if vol_toc_conf_path and await vol_toc_conf_path.exists():
            await vol_toc_conf_path.unlink()

    return vol_toc_pdf_path


async def brief_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path, doi_conference: str, absolute_pdf_link: bool):

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
        f"https://jacow.org/{doi_conference}/{f.filename}" for f in files_data
    ] if absolute_pdf_link else [
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
        author="JACoW - Joint Accelerator Conferences Website",
        producer=None,
        creator="cat--purr_meow",
        title=f"{event_title} - Proceedings at a Glance",
        format=None,
        encryption=None,
        creationDate=None,
        modDate=None,
        subject="First page only of all papers with hyperlinks to complete versions",
        keywords=None,
        trapped=None,
    )

    await pdf_unite(str(brief_pdf_path), pdf_parts, False)
    await write_metadata(metadata, str(brief_pdf_path))
    await brief_links(str(brief_pdf_path), brief_pdf_links)

    proceedings_data.proceedings_brief_size = (await brief_pdf_path.stat()).st_size


async def concat_chunks(write_path: str, pdf_files: list[str], results: list[str], first: bool, limiter: CapacityLimiter) -> None:
    async with limiter:
        results.append(write_path)
        await pdf_unite(write_path, pdf_files, first)
        # await concat_pdf(write_path, pdf_files, None)
