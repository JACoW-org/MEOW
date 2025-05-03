import logging as lg

from meow.utils.http import download_json

from anyio import CapacityLimiter, create_task_group

from anyio import create_task_group

logger = lg.getLogger(__name__)


async def collecting_event_sessions_and_contributions(
    event_id: str, event_url: str, indico_token: str
):
    """ """

    logger.info("event_final_proceedings - collecting_event_sessions_and_contributions")

    [event, settings] = await collect_event_and_settings(
        event_id, event_url, indico_token
    )
    sessions_list: list = await collect_sessions_data_list(
        event_id, event_url, indico_token
    )
    contributions_list: list = await collect_contributions_data_list(
        event_id, event_url, indico_token, sessions_list
    )

    return [event, settings, sessions_list, contributions_list]


async def collect_event_and_settings(
    event_id: str, event_url: str, indico_token: str
) -> list:
    """ """

    logger.info("event_final_proceedings - collect_event_and_settings")

    url = f"{event_url}manage/purr/settings-and-event-data"

    logger.info(url)

    response = await download_json(
        url=url, headers={"Authorization": " Bearer " + indico_token}
    )

    if "error" not in response and response.get("error") is not True:
        return [response.get("event"), response.get("settings")]

    return []


async def collect_sessions_data_list(
    event_id: str, event_url: str, indico_token: str
) -> list:
    """ """

    logger.info("event_final_proceedings - collect_sessions_data")

    url = f"{event_url}manage/purr/final-proceedings-sessions-data"

    logger.info(url)

    response = await download_json(
        url=url, headers={"Authorization": " Bearer " + indico_token}
    )

    if "error" not in response and response.get("error") is not True:
        return response.get("sessions")

    return []


async def collect_contributions_data_list(
    event_id: str, event_url: str, indico_token: str, sessions: list
) -> list:
    """ """

    contributions: list = []

    logger.info("event_final_proceedings - collect_sessions_data")

    limiter = CapacityLimiter(4)
    async with create_task_group() as tg:
        for session in sessions:
            tg.start_soon(
                collect_contributions_data_list_by_session,
                event_id,
                event_url,
                indico_token,
                session.get("id"),
                contributions,
                limiter,
            )

    return contributions


async def collect_contributions_data_list_by_session(
    event_id: str,
    event_url: str,
    indico_token: str,
    session_id: int,
    contributions: list,
    limiter: CapacityLimiter,
) -> None:
    async with limiter:
        url = (
            f"{event_url}manage/purr/final-proceedings-contributions-data/{session_id}"
        )

        logger.info(url)

        response = await download_json(
            url=url, headers={"Authorization": " Bearer " + indico_token}
        )

        if "error" not in response and response.get("error") is not True:
            contributions.extend(response.get("contributions"))
