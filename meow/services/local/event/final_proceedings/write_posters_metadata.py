import logging as lg
from typing import Callable

from anyio import Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import (
    extract_proceedings_posters,
)

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    pdf_linearize_qpdf,
)


logger = lg.getLogger(__name__)


async def write_posters_metadata(
    proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable
) -> ProceedingsData:
    """ """

    logger.info("event_final_proceedings - write_posters_metadata")

    slides_data: list[FileData] = await extract_proceedings_posters(
        proceedings_data,
        callback,
    )

    total_files: int = len(slides_data)

    logger.info(f"write_posters_metadata - files: {total_files}")

    dir_name = f"{proceedings_data.event.id}_tmp"
    pdf_cache_dir: Path = Path("var", "run", dir_name)
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    sessions_dict: dict[str, SessionData] = dict()
    for session in proceedings_data.sessions:
        sessions_dict[session.code] = session

    async with create_task_group() as tg:
        for current_slide in slides_data:
            tg.start_soon(
                write_metadata_task,
                current_slide,
                sessions_dict,
                settings,
                pdf_cache_dir,
            )

    # with start_blocking_portal() as portal:
    #     futures = [
    #         portal.start_task_soon(write_metadata_task,
    #                                current_slide, sessions_dict,
    #                                settings, pdf_cache_dir)
    #         for current_slide in slides_data
    #     ]
    #
    #     for future in as_completed(futures):
    #         pass

    return proceedings_data


async def write_metadata_task(
    current_slide: FileData, sessions, settings, pdf_cache_dir
):
    original_pdf_name = f"{current_slide.filename}"
    original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

    jacow_pdf_name = f"{current_slide.filename}_jacow"
    jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

    await jacow_pdf_file.unlink(missing_ok=True)

    # print(f"{original_pdf_file} --> {jacow_pdf_file}")

    await pdf_linearize_qpdf(str(original_pdf_file), str(jacow_pdf_file), None, None)
