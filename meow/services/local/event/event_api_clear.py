from asyncio import CancelledError
import logging as lg

from anyio import Path, create_task_group
from meow.utils.filesystem import rmtree

logger = lg.getLogger(__name__)


async def event_api_clear(event_id: int) -> None:
    """ """

    try:
        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        await _event_api_clear(event_id)

    except GeneratorExit:
        logger.error("Generator Exit")
    except CancelledError:
        logger.error("Task Cancelled")
    except BaseException as ex:
        logger.error("Generic error", exc_info=True)
        raise ex


async def _event_api_clear(event_id: int) -> None:
    """ """

    logger.info('event_api_clear - start')

    async with create_task_group() as tg:
        tg.start_soon(_event_clean_pdf_files_task, event_id)
        tg.start_soon(_event_clean_static_site_task, event_id)
        tg.start_soon(_event_clean_doi_jsons, event_id)

    logger.info('event_api_clear - end')


async def _event_clean_pdf_files_task(event_id: str) -> None:

    pdf_cache_name = f'{event_id}_tmp'
    pdf_cache_src = Path('var', 'run', pdf_cache_name)

    await rmtree(str(pdf_cache_src))


async def _event_clean_static_site_task(event_id: str) -> None:

    static_site_name = f'{event_id}_src'
    static_site_src = Path('var', 'run', static_site_name)

    site_preview_name = f'{event_id}'
    site_preview_path = Path('var', 'html', site_preview_name)

    site_archive_name = f"{event_id}.7z"
    site_archive_path = Path('var', 'html', site_archive_name)

    if await site_archive_path.exists():
        await site_archive_path.unlink()

    await rmtree(str(site_preview_path))
    await rmtree(str(static_site_src))


async def _event_clean_doi_jsons(event_id: str) -> None:

    doi_jsons_name = f'{event_id}_doi'
    doi_jsons_path = Path('var', 'run', doi_jsons_name)

    await rmtree(str(doi_jsons_path))
