import logging as lg

from meow.utils.http import download_json

from anyio import CapacityLimiter, create_task_group


logger = lg.getLogger(__name__)


async def collecting_contributions_and_files(event: dict, sessions: list, cookies: dict, settings: dict) -> list[list]:
    """ """

    logger.info('event_final_proceedings - collecting_contributions_and_files')

    contributions: list = []

    limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for session in sessions:
            tg.start_soon(download_contributions, event.get('url'), session.get('id'),
                          cookies, settings, contributions, limiter)

    # logger.info(contributions)

    return [contributions]


async def download_contributions(event_url: str, session_id: int, cookies: dict, settings: dict,
                                 contributions: list, limiter: CapacityLimiter) -> None:
    async with limiter:

        url = f"{event_url}manage/purr/final-proceedings-contributions-data/{session_id}"

        logger.info(url)

        response = await download_json(url=url, cookies=cookies)

        if 'error' not in response and response.get('error') is not True:
            contributions.extend(response.get('contributions'))
