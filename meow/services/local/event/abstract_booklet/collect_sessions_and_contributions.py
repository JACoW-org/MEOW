import logging as lg

from meow.utils.http import download_json

from anyio import CapacityLimiter, create_task_group


logger = lg.getLogger(__name__)


async def collect_sessions_and_contributions(event: dict, cookies: dict, settings: dict):
    """
    """

    event_url: str = event.get('url', '')

    sessions: list = []
    contributions: list = []

    await download_sessions(event_url, cookies, settings, sessions)

    limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for session in sessions:
            tg.start_soon(download_contributions, event_url, session.get(
                'id'), cookies, settings, contributions, limiter)

    # logger.info(sessions)
    # logger.info(contributions)

    return [sessions, contributions]


async def download_sessions(event_url: str, cookies: dict, settings: dict, sessions: list):

    response = await download_json(url=f"{event_url}manage/purr/abstract-booklet-sessions-data", cookies=cookies)

    if 'error' not in response and response.get('error') != True:
        sessions.extend(response.get('sessions'))


async def download_contributions(event_url: str, session_id: int, cookies: dict, settings: dict, contributions: list, limiter: CapacityLimiter):
    async with limiter:

        response = await download_json(url=f"{event_url}manage/purr/abstract-booklet-contributions-data/{session_id}", cookies=cookies)

        if 'error' not in response and response.get('error') != True:
            contributions.extend(response.get('contributions'))
