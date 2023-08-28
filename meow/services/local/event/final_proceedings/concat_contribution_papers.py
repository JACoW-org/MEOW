from datetime import datetime
import logging as lg

from math import sqrt
from typing import Callable

from anyio import CapacityLimiter, Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_model import AttachmentData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_papers
from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import (
    brief_links, pdf_linearize_qpdf, vol_toc_links, vol_toc_pdf, pdf_unite_pdftk)
from meow.utils.datetime import format_datetime_doi_iso
# from meow.utils.filesystem import copy
from meow.utils.list import split_list
from meow.utils.serialization import json_encode


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict,
                                     config: FinalProceedingsConfig, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name: str = f"{proceedings_data.event.id}_tmp"
    cache_dir: Path = Path('var', 'run', dir_name)
    await cache_dir.mkdir(exist_ok=True, parents=True)

    files_data = await extract_proceedings_papers(proceedings_data, callback)

    if len(files_data) > 0:

        async def _brief_task():
            await brief_pdf_task(proceedings_data, files_data, cache_dir,
                                 settings.get('doi_conference', 'CONF-YY'),
                                 config.absolute_pdf_link)

        async def _vol_task():
            await vol_pdf_task(proceedings_data, files_data, cache_dir, callback,
                               settings.get('toc_grouping', ['contribution', 'session']))

        async with create_task_group() as tg:
            tg.start_soon(_brief_task)
            tg.start_soon(_vol_task)

    return proceedings_data


async def brief_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path,
                         doi_conference: str, absolute_pdf_link: bool):

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

    brief_pdf_chunk_name = f"{event_id}_proceedings_brief_chunk.pdf"
    brief_pdf_chunk_path = Path(cache_dir, brief_pdf_chunk_name)

    brief_pdf_links_name = f"{event_id}_proceedings_brief_links.pdf"
    brief_pdf_links_path = Path(cache_dir, brief_pdf_links_name)

    brief_pdf_meta_name = f"{event_id}_proceedings_brief.pdf"
    brief_pdf_meta_path = Path(cache_dir, brief_pdf_meta_name)

    brief_pdf_files = [
        (str(Path(cache_dir, f"{f.filename}_join")))
        for f in files_data
    ]

    brief_pdf_links = [
        f"https://jacow.org/{doi_conference}/pdf/{f.filename}"
        for f in files_data
    ] if absolute_pdf_link else [
        f.filename for f in files_data
    ]

    brief_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(8)

    chunk_size = int(sqrt(len(files_data))) + 1

    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(brief_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{brief_pdf_chunk_path}." + "{:06d}".format(index),
                          vol_pdf_files_chunk, brief_pdf_results, True, capacity_limiter)

    brief_pdf_files.sort()

    pdf_parts = [str(brief_pre_pdf_path)] + brief_pdf_results \
        if brief_pre_pdf_path else brief_pdf_results

    docinfo = get_brief_metadata(event_title)
    metadata = get_brief_xmp_metadata(event_title)

    try:
        if await pdf_unite_pdftk(str(brief_pdf_chunk_path), pdf_parts, False) != 0:
            raise BaseException('Error in Proceedings at a Glance generation')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        for pdf_part in [Path(p) for p in pdf_parts]:
            if await pdf_part.exists():
                await pdf_part.unlink()

    try:
        if await brief_links(str(brief_pdf_chunk_path), str(brief_pdf_links_path), brief_pdf_links) != 0:
            raise BaseException('Error in Proceedings at a Glance links')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if await brief_pdf_chunk_path.exists():
            await brief_pdf_chunk_path.unlink()

    try:
        if await pdf_linearize_qpdf(str(brief_pdf_links_path), str(brief_pdf_meta_path), docinfo, metadata) != 0:
            raise BaseException('Error in Proceedings at a Glance clean')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if await brief_pdf_links_path.exists():
            await brief_pdf_links_path.unlink()

    proceedings_data.proceedings_brief_size = (await brief_pdf_meta_path.stat()).st_size


async def vol_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData],
                       cache_dir: Path, callback: Callable, toc_grouping: list[str]):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title

    vol_pdf_chunk_name = f"{event_id}_proceedings_volume_chunk.pdf"
    vol_pdf_chunk_path = Path(cache_dir, vol_pdf_chunk_name)

    vol_pdf_links_name = f"{event_id}_proceedings_volume_links.pdf"
    vol_pdf_links_path = Path(cache_dir, vol_pdf_links_name)

    vol_pdf_meta_name = f"{event_id}_proceedings_volume.pdf"
    vol_pdf_meta_path = Path(cache_dir, vol_pdf_meta_name)

    vol_pre_pdf_path = await get_vol_pre_pdf_path(proceedings_data, cache_dir, callback)
    [vol_toc_pdf_path, vol_toc_links_path] = await get_vol_toc_pdf_path(proceedings_data, vol_pre_pdf_path,
                                                                        cache_dir, callback, toc_grouping)

    vol_pdf_files: list[str] = [
        str(Path(cache_dir, f"{f.filename}_join"))
        for f in files_data
    ]

    vol_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(8)

    chunk_size = int(sqrt(len(files_data))) + 1

    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(vol_pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{vol_pdf_chunk_path}." + "{:06d}".format(index),
                          vol_pdf_files_chunk, vol_pdf_results, False, capacity_limiter)
        vol_pdf_results.sort()

    pdf_parts = [str(vol_pre_pdf_path)] if vol_pre_pdf_path else []
    pdf_parts = pdf_parts + [str(vol_toc_pdf_path)] if vol_toc_pdf_path else []
    pdf_parts = pdf_parts + vol_pdf_results

    docinfo = get_vol_metadata(event_title)
    metadata = get_vol_xmp_metadata(event_title)

    try:
        if await pdf_unite_pdftk(str(vol_pdf_chunk_path), pdf_parts, False) != 0:
            raise BaseException('Error in Proceedings Volume generation')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        for pdf_part in [Path(p) for p in pdf_parts]:
            if await pdf_part.exists():
                await pdf_part.unlink()

    try:
        if await vol_toc_links(str(vol_pdf_chunk_path), str(vol_pdf_links_path), str(vol_toc_links_path)) != 0:
            raise BaseException('Error in Proceedings Volume links')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if await vol_pdf_chunk_path.exists():
            await vol_pdf_chunk_path.unlink()
        if vol_toc_links_path and await vol_toc_links_path.exists():
            await vol_toc_links_path.unlink()

    try:
        if await pdf_linearize_qpdf(str(vol_pdf_links_path), str(vol_pdf_meta_path), docinfo, metadata) != 0:
            raise BaseException('Error in Proceedings Volume clean')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if await vol_pdf_links_path.exists():
            await vol_pdf_links_path.unlink()

    proceedings_data.proceedings_volume_size = (await vol_pdf_meta_path.stat()).st_size


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


async def get_vol_toc_pdf_path(proceedings_data: ProceedingsData, vol_pre_pdf_path: Path | None,
                               cache_dir: Path, callback: Callable, toc_grouping: list[str]):

    vol_toc_pdf_path: Path | None = None
    vol_toc_links_path: Path | None = None
    vol_toc_conf_path: Path | None = None

    # logger.info(toc_grouping)

    try:
        vol_toc_name = f'{proceedings_data.event.id}_proceedings_volume_toc'

        vol_toc_pdf_path = Path(cache_dir, f"{vol_toc_name}.pdf")
        vol_toc_links_path = Path(cache_dir, f"{vol_toc_name}.meta.json")
        vol_toc_conf_path = Path(cache_dir, f"{vol_toc_name}.conf.json")

        sessions = dict()

        for session in proceedings_data.sessions:
            sessions[session.code] = dict(
                session_data=session,
                contributions=[]
            )

        for contribution in proceedings_data.contributions:
            if callback(contribution) is False or contribution.session_code is None:
                continue

            if contribution.session_code in sessions:
                if len(sessions[contribution.session_code]['contributions']) == 0:
                    sessions[contribution.session_code]['page'] = contribution.page
                sessions[contribution.session_code]['contributions'].append(
                    contribution)

        toc_items = list()
        toc_settings = dict(
            include_sessions='session' in toc_grouping,
            include_contributions='contribution' in toc_grouping
        )

        for session_code, session in sessions.items():
            if toc_settings.get('include_sessions') and session.get('page', False):
                toc_items.append({'type': 'session', 'code': session_code, 'title': session.get(
                    'session_data').title, 'page': session.get('page')})

            if toc_settings.get('include_contributions'):
                for contribution in session.get('contributions'):
                    toc_items.append({'type': 'contribution', 'code': contribution.code,
                                     'title': contribution.title, 'page': contribution.page})

        # logger.info(toc_items)

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

        if await vol_toc_pdf(str(vol_toc_pdf_path), str(vol_toc_links_path), str(vol_toc_conf_path)) != 0:
            raise BaseException('Error in TOC generation')

    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        if vol_toc_conf_path and await vol_toc_conf_path.exists():
            await vol_toc_conf_path.unlink()

    return [vol_toc_pdf_path, vol_toc_links_path]


async def concat_chunks(write_path: str, pdf_files: list[str], results: list[str], first: bool,
                        limiter: CapacityLimiter) -> None:
    async with limiter:
        results.append(write_path)
        if await pdf_unite_pdftk(write_path, pdf_files, first) != 0:
            raise BaseException('Error in Proceedings Volume generation')


def get_vol_xmp_metadata(event_title):

    meta: dict = {
        'dc:title': f"{event_title} - Proceedings Volume",
        # 'dc:subject': contribution.track_meta,
        # 'dc:description': contribution.doi_data.abstract,
        'dc:language': 'en-us',
        'dc:creator': ["JACoW Conference Assembly Tool (CAT)"],
        # 'pdf:keywords': contribution.keywords_meta,
        'pdf:producer': "",
        'xmp:CreatorTool': "JACoW Conference Assembly Tool (CAT)",
        # 'xmp:Identifier': contribution.doi_data.doi_identifier,
        'xmp:ModifyDate': format_datetime_doi_iso(datetime.now()),
        'xmp:MetadataDate': format_datetime_doi_iso(datetime.now()),
        'xmp:CreateDate': format_datetime_doi_iso(datetime.now()),
    }

    return meta


def get_vol_metadata(event_title):
    # metadata = dict(
    #     author="JACoW - Joint Accelerator Conferences Website",
    #     producer=None,
    #     creator="JACoW Conference Assembly Tool (CAT)",
    #     title=f"{event_title} - Proceedings Volume",
    #     format=None,
    #     encryption=None,
    #     creationDate=None,
    #     modDate=None,
    #     subject="The complete volume of papers",
    #     keywords=None,
    #     trapped=None,
    # )

    metadata = {
        '/Author': "JACoW - Joint Accelerator Conferences Website",
        '/Producer': "",
        '/Creator': "JACoW Conference Assembly Tool (CAT)",
        '/Title': f"{event_title} - Proceedings Volume",
        '/CreationDate': format_datetime_doi_iso(datetime.now()),
        '/ModDate': format_datetime_doi_iso(datetime.now()),
        '/Subject': "The complete volume of papers",
        # '/Keywords': None
    }

    return metadata


def get_brief_xmp_metadata(event_title):

    meta: dict = {
        'dc:title': f"{event_title} - Proceedings at a Glance",
        # 'dc:subject': contribution.track_meta,
        # 'dc:description': contribution.doi_data.abstract,
        'dc:language': 'en-us',
        'dc:creator': ["JACoW Conference Assembly Tool (CAT)"],
        # 'pdf:keywords': contribution.keywords_meta,
        'pdf:producer': "",
        'xmp:CreatorTool': "JACoW Conference Assembly Tool (CAT)",
        # 'xmp:Identifier': contribution.doi_data.doi_identifier,
        'xmp:ModifyDate': format_datetime_doi_iso(datetime.now()),
        'xmp:MetadataDate': format_datetime_doi_iso(datetime.now()),
        'xmp:CreateDate': format_datetime_doi_iso(datetime.now()),
    }

    return meta


def get_brief_metadata(event_title):
    # metadata = dict(
    #     author="JACoW - Joint Accelerator Conferences Website",
    #     producer=None,
    #     creator="JACoW Conference Assembly Tool (CAT)",
    #     title=f"{event_title} - Proceedings at a Glance",
    #     format=None,
    #     encryption=None,
    #     creationDate=None,
    #     modDate=None,
    #     subject="First page only of all papers with hyperlinks to complete versions",
    #     keywords=None,
    #     trapped=None,
    # )

    metadata = {
        '/Author': "JACoW - Joint Accelerator Conferences Website",
        '/Producer': "",
        '/Creator': "JACoW Conference Assembly Tool (CAT)",
        '/Title': f"{event_title} - Proceedings at a Glance",
        '/CreationDate': format_datetime_doi_iso(datetime.now()),
        '/ModDate': format_datetime_doi_iso(datetime.now()),
        '/Subject': "The complete volume of papers",
        # '/Keywords': None
    }

    return metadata
