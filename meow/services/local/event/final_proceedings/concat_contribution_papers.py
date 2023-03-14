import logging as lg

from fitz import Document
from fitz.utils import set_metadata

from anyio import Path, create_task_group, to_process, to_thread

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def concat_contribution_papers(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    # logger.debug(f'concat_contribution_papers - files: {total_files}')

    dir_name = f"{proceedings_data.event.id}_pdf"
    file_cache_dir: Path = Path('var', 'run', dir_name)
    await file_cache_dir.mkdir(exist_ok=True, parents=True)

    volume_name = f"{proceedings_data.event.id}_proceedings_volume.pdf"
    volume_pdf: Path = Path(file_cache_dir, volume_name)

    brief_name = f"{proceedings_data.event.id}_proceedings_brief.pdf"
    brief_pdf: Path = Path(file_cache_dir, brief_name)

    await concat_volumes(proceedings_data, volume_pdf, brief_pdf, file_cache_dir)
    await stat_volumes(proceedings_data, volume_pdf, brief_pdf)

    return proceedings_data


async def concat_volumes(proceedings_data: ProceedingsData, volume_pdf: Path, brief_pdf: Path, file_cache_dir: Path):

    volume_title: str = proceedings_data.event.title

    files_data: list[FileData] = await extract_proceedings_files(proceedings_data)

    pdf_files: list[str] = [
        str(await Path(file_cache_dir, f"{c.filename}_jacow").absolute())
        for c in files_data if c is not None
    ]

    async def concat_vol_task():
        await to_process.run_sync(concat_vol, pdf_files, str(await volume_pdf.absolute()), volume_title)

    async def concat_brief_task():
        await to_process.run_sync(concat_brief, pdf_files, str(await brief_pdf.absolute()), volume_title)

    async with create_task_group() as tg:
        tg.start_soon(concat_vol_task)
        tg.start_soon(concat_brief_task)


async def stat_volumes(proceedings_data: ProceedingsData, volume_pdf: Path, brief_pdf: Path):
    async def stat_vol_task():
        proceedings_data.proceedings_volume_size = (await volume_pdf.stat()).st_size

    async def stat_brief_task():
        proceedings_data.proceedings_brief_size = (await brief_pdf.stat()).st_size

    async with create_task_group() as tg:
        tg.start_soon(stat_vol_task)
        tg.start_soon(stat_brief_task)


def concat_vol(pdf_files: list[str], full_pdf: str, volume_title: str):
    """ """

    try:
        full_doc = Document()

        for pdf_file in pdf_files:
            curr_doc = Document(filename=pdf_file)
            full_doc.insert_pdf(curr_doc, links=1, annots=1)

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

        set_metadata(full_doc, metadata)

        full_doc.save(filename=full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)


def concat_brief(pdf_files: list[str], full_pdf: str, volume_title: str):
    """ """

    try:

        full_doc = Document()

        for pdf_file in pdf_files:
            curr_doc = Document(filename=pdf_file)
            full_doc.insert_pdf(curr_doc, from_page=0,
                                to_page=0, links=1, annots=1)

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

        set_metadata(full_doc, metadata)

        full_doc.save(filename=full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)
