import logging as lg
from typing import Callable, Optional

from anyio import Path, create_task_group

from meow.services.local.event.final_proceedings.write_metadata_utils import (
    get_footer_data,
    get_header_data,
    get_metadata_pikepdf,
    get_side_data,
    get_xml_metatdata_pikepdf,
)
from meow.utils.http import download_file

from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
    ContributionPaperData,
)
from meow.models.local.event.final_proceedings.proceedings_data_utils import (
    extract_contributions_papers,
)

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    draw_frame_anyio,
    pdf_metadata_qpdf,
)


logger = lg.getLogger(__name__)


async def write_papers_metadata(
    proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable
) -> ProceedingsData:
    """ """

    logger.info("event_final_proceedings - write_papers_metadata")

    papers_data: list[ContributionPaperData] = await extract_contributions_papers(
        proceedings_data, callback
    )

    total_files: int = len(papers_data)

    logger.info(f"write_papers_metadata - files: {total_files}")

    dir_name = f"{proceedings_data.event.id}_tmp"
    pdf_cache_dir: Path = Path("var", "run", dir_name)
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    # Download license logo based on settings
    license_icon_url: Optional[str] = settings.get("paper_license_icon_url")
    if license_icon_url:
        filename = license_icon_url.split("/")[-1]
        path = Path(pdf_cache_dir, filename)
        await download_file(license_icon_url, path)

    sessions_dict: dict[int, SessionData] = dict()
    for session in proceedings_data.sessions:
        sessions_dict[session.id] = session

    async with create_task_group() as tg:
        for current_paper in papers_data:
            tg.start_soon(
                write_metadata_task,
                current_paper,
                sessions_dict,
                settings,
                pdf_cache_dir,
            )

    # with start_blocking_portal() as portal:
    #     futures = [
    #         portal.start_task_soon(write_metadata_task,
    #                                current_paper, sessions_dict,
    #                                settings, pdf_cache_dir)
    #         for current_paper in papers_data
    #     ]
    #
    #     for future in as_completed(futures):
    #         pass

    return proceedings_data


async def write_metadata_task(
    current_paper, sessions: dict[int, SessionData], settings, pdf_cache_dir
):
    contribution: ContributionData = current_paper.contribution

    session = sessions.get(contribution.session_id)

    if not session:
        return None

    current_file = current_paper.paper

    original_pdf_name = f"{current_file.filename}"
    original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

    jacow_pdf_name = f"{current_file.filename}_jacow"
    jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

    await jacow_pdf_file.unlink(missing_ok=True)

    join_pdf_name = f"{current_file.filename}_join"
    join_pdf_file = Path(pdf_cache_dir, join_pdf_name)

    await join_pdf_file.unlink(missing_ok=True)

    header_data: dict | None = get_header_data(contribution)
    footer_data: dict | None = get_footer_data(contribution, session)
    side_data = await get_side_data(settings, pdf_cache_dir)

    # metadata_mutool = get_metadata_mutool(contribution)
    metadata_pikepdf: dict | None = get_metadata_pikepdf(contribution)

    # xml_metadata_mutool = get_xml_metatdata_mutool(contribution)
    xml_metadata_pikepdf: dict | None = get_xml_metatdata_pikepdf(contribution)

    logger.info(f"preprint_marking_requested {preprint_marking_requested} / contribution.peer_reviewing_accepted {contribution.peer_reviewing_accepted} ")
    pre_print: str = (
        settings.get("pre_print", "This is a preprint")
        if contribution.peer_reviewing_accepted or preprint_marking_requested
        else ""
    )

    if pre_print != '':
         logger.info(f"code: {contribution.code} - preprint: {pre_print}")

    async def _task_jacow_files():
        await draw_frame_anyio(
            str(original_pdf_file),
            str(jacow_pdf_file),
            contribution.page,
            pre_print,
            header_data,
            footer_data,
            side_data,
            None,
            None,
            True,
        )

        await pdf_metadata_qpdf(
            str(jacow_pdf_file), metadata_pikepdf, xml_metadata_pikepdf
        )

    async def _task_concat_files():
        await draw_frame_anyio(
            str(original_pdf_file),
            str(join_pdf_file),
            contribution.page,
            pre_print,
            header_data,
            footer_data,
            side_data,
            None,
            None,
            False,
        )

    async with create_task_group() as tg:
        tg.start_soon(_task_jacow_files)
        tg.start_soon(_task_concat_files)
