
from asyncio import CancelledError
import logging as lg
from typing import Any

from anyio import Path, create_task_group


logger = lg.getLogger(__name__)


async def event_api_info(event_id: str) -> dict | None:
    """ """

    try:
        if not event_id or event_id == '':
            raise BaseException('Invalid event id')

        return await _event_api_info(event_id)

    except GeneratorExit:
        logger.error("Generator Exit")
    except CancelledError:
        logger.error("Task Cancelled")
    except BaseException as be:
        logger.error("Generic error", exc_info=True)
        raise be


async def _event_api_info(event_id: str) -> dict:
    """ """

    logger.info('event_api_info - start')

    result: dict[str, Any] = {
        'event_id': event_id,
        'pdf_cache': None,
        'pre_press': None,
        'datacite_json': None,
        'inspirehep_json': None,
        'final_proceedings': None,
        'proceedings_archive': None,
    }

    async with create_task_group() as tg:
        tg.start_soon(event_pdf_cache_info_task, event_id, result)
        tg.start_soon(event_pre_press_info_task, event_id, result)
        tg.start_soon(event_datacite_json_info_task, event_id, result)
        tg.start_soon(event_inspirehep_json_info_task, event_id, result)
        tg.start_soon(event_final_proceedings_info_task, event_id, result)
        tg.start_soon(event_proceedings_archive_info_task, event_id, result)

    logger.info('event_api_info - end')

    return dict(type='result', value=result)


async def event_pdf_cache_info_task(event_id: str, result: dict[str, Any]):
    result['pdf_cache'] = await Path('var', 'run', f"{event_id}_tmp").exists()


async def event_pre_press_info_task(event_id: str, result: dict[str, Any]):
    result['pre_press'] = await Path('var', 'html', f"{event_id}", 'prepress').exists()


async def event_datacite_json_info_task(event_id: str, result: dict[str, Any]):
    result['datacite_json'] = await Path('var', 'run', f"{event_id}_doi").exists()


async def event_inspirehep_json_info_task(event_id: str, result: dict[str, Any]):
    result['datacite_json'] = await Path('var', 'run', f"{event_id}_doi").exists()


async def event_final_proceedings_info_task(event_id: str, result: dict[str, Any]):
    result['final_proceedings'] = await Path('var', 'html', f"{event_id}", 'proceedings').exists()


async def event_proceedings_archive_info_task(event_id: str, result: dict[str, Any]):
    result['proceedings_archive'] = await Path('var', 'html', f"{event_id}.7z").exists()
