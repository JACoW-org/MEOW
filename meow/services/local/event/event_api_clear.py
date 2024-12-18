from asyncio import CancelledError
import logging as lg

from anyio import Path, create_task_group
from meow.utils.filesystem import rmtree

logger = lg.getLogger(__name__)


async def event_api_clear(event_id: str) -> None:
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


async def _event_api_clear(event_id: str) -> None:
    """ """

    logger.info('event_api_clear - start')

    async with create_task_group() as tg:
        tg.start_soon(_event_clean_pdf_files_task, event_id)
        tg.start_soon(_event_clean_static_site_task, event_id)
        tg.start_soon(_event_clean_doi_jsons, event_id)
        tg.start_soon(_event_clean_hep_jsons, event_id)

    logger.info('event_api_clear - end')


async def _event_clean_pdf_files_task(event_id: str) -> None:

    pdf_cache_name = f'{event_id}_tmp'
    pdf_cache_src = Path('var', 'run', pdf_cache_name)

    await rmtree(str(pdf_cache_src))


async def _event_clean_static_site_task(event_id: str) -> None:

    site_sources_path = Path('var', 'run', f'{event_id}_src')
    site_preview_path = Path('var', 'html', f'{event_id}')
    site_archive_path = Path('var', 'html', f"{event_id}.7z")

    await site_archive_path.unlink(missing_ok=True)

    if await site_preview_path.exists():
        await rmtree(str(site_preview_path))

    if await site_sources_path.exists():
        await rmtree(str(site_sources_path))


async def _event_clean_doi_jsons(event_id: str) -> None:

    doi_jsons_name = f'{event_id}_doi'
    doi_jsons_path = Path('var', 'run', doi_jsons_name)

    await rmtree(str(doi_jsons_path))


async def _event_clean_hep_jsons(event_id: str) -> None:

    hep_jsons_name = f'{event_id}_hep'
    hep_jsons_path = Path('var', 'run', hep_jsons_name)

    await rmtree(str(hep_jsons_path))
