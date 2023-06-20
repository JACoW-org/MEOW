import logging as lg

from anyio import Path, create_task_group, CapacityLimiter
from anyio import create_memory_object_stream, ClosedResourceError, EndOfStream
from anyio.streams.memory import MemoryObjectSendStream
from meow.app.errors.service_error import ServiceError
from meow.models.local.common.auth import BasicAuthData

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.tasks.local.doi.utils import generate_doi_identifier

from meow.utils.http import put_json


logger = lg.getLogger(__name__)


async def draft_contribution_doi(proceedings_data: ProceedingsData, cookies: dict, settings: dict):
    """ """

    logger.info('draft_contribution_doi - draft_contribution_doi')

    doi_dir = Path('var', 'run', f'{proceedings_data.event.id}_doi')
    dir_exists = await doi_dir.exists()
    if not dir_exists:
        raise ServiceError("doi_dir not exists")

    results: list[dict] = []

    contributions_data: list[ContributionData] = [
        c for c in proceedings_data.contributions
    ]

    total_contributions: int = len(contributions_data)

    logger.info(f'draft_contribution_doi - ' +
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

                    if len(results) >= total_contributions:
                        receive_stream.close()

        except ClosedResourceError as crs:
            logger.debug(crs, exc_info=False)
        except EndOfStream as eos:
            logger.debug(eos, exc_info=False)
        except BaseException as ex:
            logger.error(ex, exc_info=True)

    return results


async def _doi_task(capacity_limiter: CapacityLimiter, total: int, index: int,
                    contribution: ContributionData, cookies: dict, settings: dict,
                    doi_dir: Path, stream: MemoryObjectSendStream) -> None:
    """ """

    async with capacity_limiter:

        response: str | None = None
        error: str | None = None

        try:

            doi_file = Path(doi_dir, f'{contribution.code}.json')

            doi_exists = await doi_file.exists()

            if doi_exists:

                logger.info(str(doi_file))

                doi_json = await doi_file.read_text()

                doi_identifier: str = generate_doi_identifier(
                    context=settings.get('doi_context', '10.18429'),
                    organization=settings.get('doi_organization', 'JACoW'),
                    conference=settings.get('doi_conference', 'CONF-YY'),
                    contribution=contribution.code
                )

                proto = f"https:"
                host = f"api.test.datacite.org"
                context = f"dois"
                path = f"{doi_identifier}"

                doi_url = f"{proto}//{host}/{context}/{path}".lower()

                logger.info(f"{doi_file} -> {doi_url}")

                # logger.info(doi_data)
                # logger.info(doi_json)

                auth = BasicAuthData(login='CERN.JACOW',
                                     password='DataCite.cub-gwd')

                headers = {'Content-Type': 'application/vnd.api+json'}

                response = await put_json(url=doi_url, body=doi_json, headers=headers, auth=auth)

        except BaseException as ex:
            error = str(ex)
            logger.error(ex, exc_info=True)

        await send_res(stream, total, index, contribution, response=response, error=error)


async def send_res(stream: MemoryObjectSendStream, total, index, contribution, response, error=None):
    await stream.send({
        "total": total,
        "index": index,
        "contribution": contribution,
        "response": response,
        "error": error
    })
