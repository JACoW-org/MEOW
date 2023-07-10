import logging as lg

from meow.utils.http import download_json

from anyio import create_task_group

logger = lg.getLogger(__name__)


async def collecting_sessions_and_attachments(event: dict, cookies: dict, settings: dict) -> list[list]:
    """ """

    logger.info('event_final_proceedings - collecting_sessions_and_attachments')

    sessions: list = []
    attachments: list = []

    async with create_task_group() as tg:
        tg.start_soon(download_sessions, event.get(
            'url'), cookies, settings, sessions)
        tg.start_soon(download_attachments, event.get(
            'url'), cookies, settings, attachments)

    # logger.info(sessions)
    # logger.info(attachments)

    return [sessions, attachments]


async def download_sessions(event_url: str, cookies: dict, settings: dict, sessions: list) -> None:

    url = f"{event_url}manage/purr/final-proceedings-sessions-data"

    logger.info(url)

    response = await download_json(url=url, cookies=cookies)

    if 'error' not in response and response.get('error') is not True:
        sessions.extend(response.get('sessions'))


async def download_attachments(event_url: str, cookies: dict, settings: dict, attachments: list) -> None:

    url = f"{event_url}manage/purr/final-proceedings-attachments-data"

    logger.info(url)

    response = await download_json(url=url, cookies=cookies)

    if 'error' not in response and response.get('error') is not True:
        attachments.extend(response.get('attachments'))
