import logging as lg
from typing import Any

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream
from meow.app.errors.service_error import ServiceError
from meow.models.local.common.auth import BasicAuthData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.services.local.event.doi.event_doi_utils import get_doi_api_login, get_doi_api_password, get_doi_api_url
from meow.tasks.local.doi.utils import generate_doi_identifier

from meow.utils.http import fetch_json


logger = lg.getLogger(__name__)


async def get_contribution_doi(proceedings_data: ProceedingsData, cookies: dict, settings: dict):
    """ """

    logger.info('get_contribution_doi - get_contribution_doi')

    doi_dir = Path('var', 'run', f'{proceedings_data.event.id}_doi')
    dir_exists = await doi_dir.exists()
    if not dir_exists:
        raise ServiceError("doi_dir not exists")

    results: list[dict] = []

    contributions_data: list[ContributionData] = [
        c for c in proceedings_data.contributions
        if await Path(doi_dir, f'{c.code}.json').exists()
    ]

    total_contributions: int = len(contributions_data)

    logger.info(f'get_contribution_doi - ' +
                f'contributions: {total_contributions}')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_contribution in enumerate(contributions_data):
                tg.start_soon(_doi_task, capacity_limiter, total_contributions,
                              current_index, current_contribution, cookies, settings,
                              doi_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for result in receive_stream:

                    results.append(result)

                    logger.info(f"elaborated: {len(results)}" +
                                f" - {total_contributions}")

                    yield result

                    if len(results) >= total_contributions:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except BaseException as ex:
            logger.error(ex, exc_info=True)


async def _doi_task(capacity_limiter: CapacityLimiter, total: int, index: int,
                    contribution: ContributionData, cookies: dict, settings: dict,
                    doi_dir: Path, stream: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        doi_identifier: str | None = None
        response: str | None = None
        error: str | None = None

        try:

            doi_file = Path(doi_dir, f'{contribution.code}.json')

            # logger.info(str(doi_file))

            doi_identifier: str | None = generate_doi_identifier(
                context=settings.get('doi_context', '10.18429'),
                organization=settings.get('doi_organization', 'JACoW'),
                conference=settings.get('doi_conference', 'CONF-YY'),
                contribution=contribution.code
            )

            doi_user = get_doi_api_login(settings=settings)
            doi_password = get_doi_api_password(settings=settings)
            doi_api_url = get_doi_api_url(settings=settings,
                                          doi_id=doi_identifier)

            logger.info(f"{doi_file} -> {doi_api_url}")

            # logger.info(doi_data)
            # logger.info(doi_json)

            auth = BasicAuthData(login=doi_user, password=doi_password)

            headers = {'accept': 'application/vnd.api+json'}

            response = await fetch_json(url=doi_api_url, headers=headers, auth=auth)

        except BaseException as ex:
            if ex.args:
                error = ex.args[0].get('code')
            logger.error(ex, exc_info=True)

        await send_res(stream, total, index, contribution, doi_identifier, response=response, error=error)


async def send_res(stream: MemoryObjectSendStream, total: int, index: int, contribution: ContributionData,
                   doi_identifier: str | None, response: Any, error=None):

    doi = response.get('data', None) if response else None

    await stream.send({
        "total": total,
        "index": index,
        "code": contribution.code,
        "id": doi_identifier,
        "doi": doi,
        "error": error
    })
