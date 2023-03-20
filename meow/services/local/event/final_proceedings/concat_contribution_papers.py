import logging as lg

from anyio import Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_utils import extract_proceedings_files
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.services.local.event.event_pdf_utils import write_metadata
from meow.utils.process import run_cmd


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

    # pdf_files: list[str] = [
    #     str(await Path(file_cache_dir, f"{c.filename}_jacow").absolute())
    #     for c in files_data if c is not None
    # ]
    # 
    # await to_process.run_sync(concat_vol, pdf_files, str(await volume_pdf.absolute()), volume_title)
    # await to_process.run_sync(concat_brief, pdf_files, str(await brief_pdf.absolute()), volume_title)
    
    # async def concat_vol_task():
    #     await to_process.run_sync(concat_vol, pdf_files, str(await volume_pdf.absolute()), volume_title)
    # 
    # async def concat_brief_task():
    #     await to_process.run_sync(concat_brief, pdf_files, str(await brief_pdf.absolute()), volume_title)
    # 
    # async with create_task_group() as tg:
    #     tg.start_soon(concat_vol_task)
    #     tg.start_soon(concat_brief_task)
    
    cache_pdf_path = str(await file_cache_dir.absolute())
    meow_cli_path = str(await Path("meow.py").absolute())    
    venv_py_path = str(await Path("venv", "bin", "python3").absolute())
    
    # volume_pdf_path = str(await volume_pdf.absolute())
    # brief_pdf_path = str(await brief_pdf.absolute())

    volume_pdf_cmd = [venv_py_path, meow_cli_path, "join", "-o", f"{volume_pdf.name}"]
    brief_pdf_cmd = [venv_py_path, meow_cli_path, "join", "-o", f"{brief_pdf.name}"]
    
    for file_data in files_data:
        if file_data is not None:
            file_name = f"{file_data.filename}_jacow"
            volume_pdf_cmd.append(f"{file_name}")
            brief_pdf_cmd.append(f"{file_name},,1")
    
    # await run_cmd(cache_pdf_path, volume_pdf_cmd)
    # await run_cmd(cache_pdf_path, brief_pdf_cmd)
    
    async with create_task_group() as tg:
        tg.start_soon(run_cmd, volume_pdf_cmd, cache_pdf_path)
        tg.start_soon(run_cmd, brief_pdf_cmd, cache_pdf_path)
           
    async with create_task_group() as tg:
        tg.start_soon(metadata_vol, str(await volume_pdf.absolute()), volume_title)
        tg.start_soon(metadata_brief, str(await brief_pdf.absolute()), volume_title)
    
    # volume_pdf_cmd = ["convert"]
    # brief_pdf_cmd = ["convert"]
    # 
    # for file_data in files_data:
    #     if file_data is not None:
    #         file_name = f"{file_data.filename}_jacow"
    #         file_path = f"{file_name}"
    #         volume_pdf_cmd.append(f"{file_path}")
    #         brief_pdf_cmd.append(f"{file_path}[0,1]")
    #         
    # volume_pdf_cmd.append(f"{volume_pdf.name}")
    # brief_pdf_cmd.append(f"{brief_pdf.name}")
    #   
    # await run_cmd(cache_pdf_path, volume_pdf_cmd)
    # await run_cmd(cache_pdf_path, brief_pdf_cmd)


async def stat_volumes(proceedings_data: ProceedingsData, volume_pdf: Path, brief_pdf: Path):
    async def stat_vol_task():
        proceedings_data.proceedings_volume_size = (await volume_pdf.stat()).st_size

    async def stat_brief_task():
        proceedings_data.proceedings_brief_size = (await brief_pdf.stat()).st_size

    async with create_task_group() as tg:
        tg.start_soon(stat_vol_task)
        tg.start_soon(stat_brief_task)


async def metadata_vol(full_pdf: str, volume_title: str):
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

        logger.info(metadata)

        await write_metadata(metadata, full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)



async def metadata_brief(full_pdf: str, volume_title: str):
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

        logger.info(metadata)

        await write_metadata(metadata, full_pdf)

    except Exception as e:
        logger.error(e, exc_info=True)

