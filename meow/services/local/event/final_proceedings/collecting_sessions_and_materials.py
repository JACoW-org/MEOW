import logging as lg

from meow.utils.http import download_json

from anyio import create_task_group

logger = lg.getLogger(__name__)


async def collecting_sessions_and_materials(event: dict, cookies: dict, settings: dict) -> list[list]:
    """ """

    logger.info('event_final_proceedings - collecting_sessions_and_materials')

    sessions: list = []
    materials: list = []

    async with create_task_group() as tg:
        tg.start_soon(download_sessions, event.get(
            'url'), cookies, settings, sessions)
        tg.start_soon(download_materials, event.get(
            'url'), cookies, settings, materials)

    return [sessions, materials]


async def download_sessions(event_url: str, cookies: dict, settings: dict, sessions: list) -> None:

    url = f"{event_url}manage/purr/final-proceedings-sessions-data"

    logger.info(url)

    response = await download_json(url=url, cookies=cookies)

    if 'error' not in response and response.get('error') is not True:
        sessions.extend(response.get('sessions'))


async def download_materials(event_url: str, cookies: dict, settings: dict, materials: list) -> None:

    url = f"{event_url}manage/purr/final-proceedings-attachments-data"

    logger.info(url)

    response = await download_json(url=url, cookies=cookies)

    if 'error' not in response and response.get('error') is not True:
        indico_materials = response.get('attachments', [])
        for purr_material in settings.get('materials', []):
            for indico_material in indico_materials:
                if indico_material.get('id') == purr_material.get('id'):
                    indico_material['section'] = purr_material.get('section')
                    indico_material['index'] = purr_material.get('index')
                    materials.append(indico_material)
