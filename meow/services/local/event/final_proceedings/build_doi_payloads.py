import logging as lg

from anyio import create_task_group, CapacityLimiter, Path

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.tasks.local.doi.models import ContributionDOI
from meow.utils.filesystem import rmtree

logger = lg.getLogger(__name__)


async def build_doi_payloads(proceedings_data: ProceedingsData) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - build_doi_payloads')

    doi_dir = Path('var', 'run', f'{proceedings_data.event.id}_doi')

    if await doi_dir.exists():
        await rmtree(str(doi_dir))

    await doi_dir.mkdir(exist_ok=True, parents=True)

    total_contributions: int = len(proceedings_data.contributions)

    logger.info('build_doi_payloads - '
                + f'contributions: {total_contributions}')

    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:

        # conference DOI
        tg.start_soon(generate_conference_doi_payload_task,
                      capacity_limiter, proceedings_data, doi_dir)

        # contributions DOIs
        for contribution in proceedings_data.contributions:
            if contribution.doi_data:
                tg.start_soon(generate_doi_payload_task,
                              capacity_limiter, contribution.doi_data, doi_dir)

    return proceedings_data


async def generate_conference_doi_payload_task(capacity_limiter: CapacityLimiter,
                                               proceedings_data: ProceedingsData,
                                               doi_dir: Path) -> None:

    """ """

    async with capacity_limiter:
        doi_file = Path(doi_dir, f'{proceedings_data.event.id}.json')

        await doi_file.unlink(missing_ok=True)

        # JSON string
        payload = proceedings_data.conference_doi_payload

        # write to file
        await doi_file.write_text(payload)


async def generate_doi_payload_task(capacity_limiter: CapacityLimiter,
                                    contribution_doi: ContributionDOI,
                                    doi_dir: Path) -> None:
    """ """

    async with capacity_limiter:

        doi_file = Path(doi_dir, f'{contribution_doi.code}.json')

        await doi_file.unlink(missing_ok=True)

        # generate JSON string
        json_text = contribution_doi.as_json()

        # write to a file
        await doi_file.write_text(json_text)
