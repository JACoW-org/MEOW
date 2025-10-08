import logging as lg

from meow.services.local.event.doi.event_doi_utils import (
    get_doi_api_login,
    get_doi_api_password,
    get_doi_login_url,
)

from meow.utils.http import http_post


logger = lg.getLogger(__name__)


async def http_datacite_login(settings: dict):
    """ """

    logger.info("http_datacite_login")

    try:
        result: dict = dict()

        doi_user = get_doi_api_login(settings=settings)
        doi_password = get_doi_api_password(settings=settings)
        doi_api_url = get_doi_login_url(settings=settings)

        logger.info(f"doi_user={doi_user}")
        logger.info(f"doi_password={doi_password}")
        logger.info(f"doi_api_url={doi_api_url}")

        data = {
            "grant_type": "password",
            "username": doi_user,
            "password": doi_password,
        }

        result = await http_post(url=doi_api_url, data=data)

        return result

    except BaseException as be:
        logger.error(be, exc_info=True)

        raise BaseException(
            dict(
                message="Wrong account ID or password",
            )
        )
