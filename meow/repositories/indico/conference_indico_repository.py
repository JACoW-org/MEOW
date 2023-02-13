from typing import Any

from meow.services.local.settings.find_settings import get_local_settings
from meow.utils.http import download_json


async def get_indico_conference_data(conference_id: str) -> Any:
    """ """

    settings = await get_local_settings()

    # FIXME: indico export url -> settings
    conference_url: str = f"{settings.indico_http_url}/export/event/{conference_id}.json?detail=sessions"
    conference_raw = await download_json(url=conference_url)
    conference_data = conference_raw['results'][0]

    return conference_data
