from datetime import datetime
import logging as lg

from math import sqrt
from typing import Callable

from anyio import CapacityLimiter, Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.event_model import MaterialData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_papers
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsConfig
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    brief_links, pdf_linearize_qpdf, vol_toc_links, vol_toc_pdf, pdf_unite_pdftk)
from meow.utils.datetime import format_datetime_doi_iso
# from meow.utils.filesystem import copy
from meow.utils.list import split_list
from meow.utils.serialization import json_encode


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict,
                                     config: ProceedingsConfig, callback: Callable) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - concat_contribution_papers')

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    doi_conf = settings.get('doi_conference', 'CONF-YY')
    toc_grouping = settings.get('toc_grouping', ['contribution', 'session'])

    dir_name: str = f"{proceedings_data.event.id}_tmp"
    cache_dir: Path = Path('var', 'run', dir_name)
    await cache_dir.mkdir(exist_ok=True, parents=True)

    files_data = await extract_proceedings_papers(proceedings_data, callback)

    if len(files_data) > 0:

        # async def _brief_task():
        #     await brief_pdf_task(proceedings_data, files_data, cache_dir,
        #                          settings.get('doi_conference', 'CONF-YY'),
        #                          config.absolute_pdf_link)

        # async def _vol_task():
        #     await vol_pdf_task(proceedings_data, files_data, cache_dir, callback,
        #                        settings.get('toc_grouping', ['contribution', 'session']))

        # async with create_task_group() as tg:
        #     tg.start_soon(_brief_task)
        #     tg.start_soon(_vol_task)

        await brief_pdf_task(proceedings_data, files_data, cache_dir,
                             doi_conf, config.absolute_pdf_link)

        await vol_pdf_task(proceedings_data, files_data, cache_dir,
                           callback, toc_grouping)

        await unlink_files(files_data, cache_dir)

    return proceedings_data


async def get_pdf_files(cache_dir: Path, files_data: list[FileData]) -> list[str]:
    pdf_files: list[str] = []

    for f in files_data:
        p = Path(cache_dir, f"{f.filename}_join")
        if await p.exists():
            pdf_files.append(str(p))

    return pdf_files


async def brief_pdf_task(proceedings_data: ProceedingsData, files_data: list[FileData], cache_dir: Path,
                         doi_conference: str, absolute_pdf_link: bool):

    event_id = proceedings_data.event.id
    event_title = proceedings_data.event.title

    brief_pre_pdf_path: Path | None = None

    try:

        materials_data: list[MaterialData] = proceedings_data.materials
        for material_data in materials_data:

            if material_data.section == 'at-a-glance-cover':
                brief_pre_pdf_path = Path(cache_dir, material_data.filename)

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

    brief_pdf_links = [
        f"https://jacow.org/{doi_conference}/pdf/{f.filename}"
        for f in files_data
    ] if absolute_pdf_link else [
        f.filename for f in files_data
    ]

    brief_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(12)

    chunk_size = int(sqrt(len(files_data))) + 1

    pdf_files: list[str] = await get_pdf_files(cache_dir, files_data)

    # logger.info("BRIEF_PDF" + json_encode(pdf_files).decode('utf-8'))

    async with create_task_group() as tg:
        for index, vol_pdf_files_chunk in enumerate(split_list(pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{brief_pdf_chunk_path}." + "{:06d}".format(index),
                          vol_pdf_files_chunk, brief_pdf_results, True, capacity_limiter)

    brief_pdf_results.sort()

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
            await pdf_part.unlink(missing_ok=True)

    try:
        if await brief_links(str(brief_pdf_chunk_path), str(brief_pdf_links_path), brief_pdf_links) != 0:
            raise BaseException('Error in Proceedings at a Glance links')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        await brief_pdf_chunk_path.unlink(missing_ok=True)

    try:
        if await pdf_linearize_qpdf(str(brief_pdf_links_path), str(brief_pdf_meta_path), docinfo, metadata) != 0:
            raise BaseException('Error in Proceedings at a Glance clean')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        await brief_pdf_links_path.unlink(missing_ok=True)

    proceedings_data.proceedings_brief_size = (await brief_pdf_meta_path.stat()).st_size

    logger.info(
        f"proceedings_brief_size: {proceedings_data.proceedings_brief_size}")


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

    vol_pre_pdf_path = await get_vol_pre_pdf_path(proceedings_data, cache_dir)
    [vol_toc_pdf_path, vol_toc_links_path] = await get_vol_toc_pdf_path(proceedings_data, vol_pre_pdf_path,
                                                                        cache_dir, callback, toc_grouping)

    vol_pdf_results: list[str] = []

    capacity_limiter = CapacityLimiter(12)

    chunk_size = int(sqrt(len(files_data))) + 1

    pdf_files: list[str] = await get_pdf_files(cache_dir, files_data)

    # logger.info("VOL_PDF" + json_encode(pdf_files).decode('utf-8'))

    async with create_task_group() as tg:
        for index, pdf_files_chunk in enumerate(split_list(pdf_files, chunk_size)):
            tg.start_soon(concat_chunks, f"{vol_pdf_chunk_path}." + "{:06d}".format(index),
                          pdf_files_chunk, vol_pdf_results, False, capacity_limiter)

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
            await pdf_part.unlink(missing_ok=True)

    try:
        if await vol_toc_links(str(vol_pdf_chunk_path), str(vol_pdf_links_path), str(vol_toc_links_path)) != 0:
            raise BaseException('Error in Proceedings Volume links')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        await vol_pdf_chunk_path.unlink(missing_ok=True)
        await vol_toc_links_path.unlink(missing_ok=True)

    try:
        if await pdf_linearize_qpdf(str(vol_pdf_links_path), str(vol_pdf_meta_path), docinfo, metadata) != 0:
            raise BaseException('Error in Proceedings Volume clean')
    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        await vol_pdf_links_path.unlink(missing_ok=True)

    proceedings_data.proceedings_volume_size = (await vol_pdf_meta_path.stat()).st_size

    logger.info(
        f"proceedings_volume_size: {proceedings_data.proceedings_volume_size}")


async def unlink_files(files_data: list[FileData], cache_dir: Path):

    pdf_files: list[str] = await get_pdf_files(cache_dir, files_data)

    async def _unlink_file(vol_pdf: Path):
        await vol_pdf.unlink(missing_ok=True)

    async with create_task_group() as tg:
        for vol_pdf in [Path(p) for p in pdf_files]:
            tg.start_soon(_unlink_file, vol_pdf)


async def get_vol_pre_pdf_path(proceedings_data: ProceedingsData, cache_dir: Path):
    vol_pre_pdf_path: Path | None = None

    try:
        materials_data: list[MaterialData] = proceedings_data.materials
        for material_data in materials_data:

            if material_data.section == 'final-proceedings-cover':
                vol_pre_pdf_path = Path(cache_dir, material_data.filename)

                if not await vol_pre_pdf_path.exists():
                    vol_pre_pdf_path = None

    except Exception as e:
        logger.error(e, exc_info=True)

    return vol_pre_pdf_path


async def get_vol_toc_pdf_path(proceedings_data: ProceedingsData, vol_pre_pdf_path: Path | None,
                               cache_dir: Path, callback: Callable, toc_grouping: list[str]):

    session_ids = dict()
    toc_items = list()

    vol_toc_name = f'{proceedings_data.event.id}_proceedings_volume_toc'

    vol_toc_pdf_path = Path(cache_dir, f"{vol_toc_name}.pdf")
    vol_toc_links_path = Path(cache_dir, f"{vol_toc_name}.meta.json")
    vol_toc_conf_path = Path(cache_dir, f"{vol_toc_name}.conf.json")

    # logger.info(toc_grouping)

    try:

        for session in proceedings_data.sessions:
            session_ids[session.id] = dict(
                session_data=session,
                contributions=[],
                page=0
            )

        for contribution in proceedings_data.contributions:
            if callback(contribution) is False or not contribution.session_code:
                continue

            if contribution.session_id in session_ids:
                session_dict = session_ids[contribution.session_id]
                if len(session_dict['contributions']) == 0:
                    session_dict['page'] = contribution.page
                session_dict['contributions'].append(contribution)

        toc_settings = dict(
            include_sessions='session' in toc_grouping,
            include_contributions='contribution' in toc_grouping
        )

        for session_id, session in session_ids.items():
            if toc_settings.get('include_sessions') and session.get('page', False):
                current = {
                    'type': 'session',
                    'id': session_id,
                    'code': session.get('code'),
                    'title': session.get('session_data').title,
                    'page': session.get('page')
                }

                toc_items.append(current)

            if toc_settings.get('include_contributions'):
                for contribution in session.get('contributions'):
                    current = {
                        'type': 'contribution',
                        'code': contribution.code,
                        'title': contribution.title,
                        'page': contribution.page
                    }

                    toc_items.append(current)

        # logger.info(toc_items)

        toc_data: dict = {
            "toc_title": "Table of Contents",
            "pre_pdf": str(vol_pre_pdf_path) if vol_pre_pdf_path else None,
            "vol_file": f"{proceedings_data.event.id}_proceedings_volume.pdf",
            "toc_items": toc_items,
            "toc_settings": toc_settings,
            "event": {
                "name": proceedings_data.event.name,
                "title": proceedings_data.event.title,
                "series": proceedings_data.event.series,
                "isbn": proceedings_data.event.isbn,
                "doi": proceedings_data.event.doi_label,
                "issn": proceedings_data.event.issn,
            }
        }

        await vol_toc_conf_path.write_text(json_encode(toc_data).decode('utf-8'))

        if await vol_toc_pdf(str(vol_toc_pdf_path), str(vol_toc_links_path), str(vol_toc_conf_path)) != 0:
            raise BaseException('Error in TOC generation')

    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        await vol_toc_conf_path.unlink(missing_ok=True)

    return [vol_toc_pdf_path, vol_toc_links_path]


async def concat_chunks(write_path: str, pdf_files: list[str], results: list[str], first: bool,
                        limiter: CapacityLimiter) -> None:
    async with limiter:
        results.append(write_path)
        if await pdf_unite_pdftk(write_path, pdf_files, first) != 0:
            raise BaseException('Error in Proceedings Volume generation')


def get_vol_xmp_metadata(event_title):
    """ https://developer.adobe.com/xmp/docs/XMPNamespaces/dc/ """

    meta: dict = {
        'dc:title': f"{event_title} - Proceedings Volume",
        'dc:subject': "Proceedings Volume",
        # 'dc:description': contribution.doi_data.abstract,
        'dc:language': 'en-us',
        'dc:creator': ["JACoW - Joint Accelerator Conferences Website"],
        # 'pdf:keywords': contribution.keywords_meta,
        # 'pdf:producer': "JACoW Conference Assembly Tool (CAT)",
        'xmp:CreatorTool': "JACoW Conference Assembly Tool (CAT)",
        # 'xmp:Identifier': contribution.doi_data.doi_identifier,
        'xmp:ModifyDate': format_datetime_doi_iso(datetime.now()),
        # 'xmp:MetadataDate': format_datetime_doi_iso(datetime.now()),
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
        '/Producer': "JACoW Conference Assembly Tool (CAT)",
        '/Creator': "JACoW Conference Assembly Tool (CAT)",
        '/Title': f"{event_title} - Proceedings Volume",
        '/CreationDate': format_datetime_doi_iso(datetime.now()),
        '/ModDate': format_datetime_doi_iso(datetime.now()),
        '/Subject': "The complete volume of papers",
        '/Keywords': f"JACoW, {event_title}, Proceedings"
    }

    return metadata


def get_brief_xmp_metadata(event_title):
    """ https://developer.adobe.com/xmp/docs/XMPNamespaces/dc/ """

    meta: dict = {
        'dc:title': f"{event_title} - Proceedings at a Glance",
        'dc:subject': "Proceedings at a Glance",
        # 'dc:description': contribution.doi_data.abstract,
        'dc:language': 'en-us',
        'dc:creator': ["JACoW - Joint Accelerator Conferences Website"],
        'pdf:keywords': f"JACoW, {event_title}, Proceedings at a Glance",
        # 'pdf:producer': "",
        'xmp:CreatorTool': "JACoW Conference Assembly Tool (CAT)",
        # 'xmp:Identifier': contribution.doi_data.doi_identifier,
        'xmp:ModifyDate': format_datetime_doi_iso(datetime.now()),
        # 'xmp:MetadataDate': format_datetime_doi_iso(datetime.now()),
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
        '/Producer': "JACoW Conference Assembly Tool (CAT)",
        '/Creator': "JACoW Conference Assembly Tool (CAT)",
        '/Title': f"{event_title} - Proceedings at a Glance",
        '/CreationDate': format_datetime_doi_iso(datetime.now()),
        '/ModDate': format_datetime_doi_iso(datetime.now()),
        '/Subject': "First page only of all papers with hyperlinks to complete versions",
        '/Keywords': f"JACoW, {event_title}, Proceedings at a Glance"
    }

    return metadata
