import logging as lg

from meow.utils.http import download_json

from anyio import create_task_group

logger = lg.getLogger(__name__)


async def collecting_sessions_and_attachments(event: dict, cookies: dict, settings: dict) -> list[list]:
    """ """

    sessions: list = []
    attachments: list = []

    async with create_task_group() as tg:
        tg.start_soon(download_sessions, event.get('url'), cookies, settings, sessions)
        tg.start_soon(download_attachments, event.get('url'), cookies, settings, attachments)

    # logger.info(sessions)
    # logger.info(attachments)

    return [sessions, attachments]


async def download_sessions(event_url: str, cookies: dict, settings: dict, sessions: list):

    response = await download_json(url=f"{event_url}/manage/purr/abstract-booklet-sessions-data", cookies=cookies)

    if 'error' not in response and response.get('error') != True:
        sessions.extend(response.get('sessions'))


async def download_attachments(event_url: str, cookies: dict, settings: dict, attachments: list):

    response = await download_json(url=f"{event_url}/manage/purr/final-proceedings-attachments-data", cookies=cookies)

    if 'error' not in response and response.get('error') != True:
        attachments.extend(response.get('attachments'))
