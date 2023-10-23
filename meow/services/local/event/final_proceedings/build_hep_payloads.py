import logging as lg

from anyio import open_file, create_task_group, CapacityLimiter, Path

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.tasks.local.doi.models import ContributionDOI
from meow.utils.filesystem import rmtree

logger = lg.getLogger(__name__)


async def build_hep_payloads(proceedings_data: ProceedingsData) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - build_hep_payloads')

    hep_name = f'{proceedings_data.event.id}_hep'
    hep_dir = Path('var', 'run', f'{hep_name}')
    hep_file = Path(hep_dir, 'inspirehep.jsonl')

    if await hep_dir.exists():
        await rmtree(str(hep_dir))

    await hep_dir.mkdir(exist_ok=True, parents=True)

    total_contributions: int = len(proceedings_data.contributions)

    logger.info('build_hep_payloads - '
                + f'contributions: {total_contributions}')

    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:

        # conference DOI
        tg.start_soon(generate_conference_hep_payload_task,
                      capacity_limiter, proceedings_data, hep_dir)

        # contributions DOIs
        for contribution in proceedings_data.contributions:
            if contribution.doi_data is not None:
                tg.start_soon(generate_hep_payload_task,
                              capacity_limiter, contribution.doi_data, hep_dir)

    await concat_hep_files(proceedings_data, hep_dir, hep_file)

    return proceedings_data


async def concat_hep_files(proceedings_data: ProceedingsData,
                           hep_dir: Path,
                           hep_file: Path):

    hep_event_path = [
        Path(hep_dir, f'{proceedings_data.event.id}.json')
    ]

    hep_contrib_paths = [
        Path(hep_dir, f'{contribution.code}.json')
        for contribution in proceedings_data.contributions
        if contribution.doi_data is not None
    ]

    hep_paths = hep_event_path + hep_contrib_paths

    async with await open_file(str(hep_file), 'a+') as f:
        for p in hep_paths:
            async with await open_file(str(p)) as c:
                json = await c.read()
                await f.write(f'{json}\n')


async def generate_conference_hep_payload_task(capacity_limiter: CapacityLimiter,
                                               proceedings_data: ProceedingsData,
                                               hep_dir: Path) -> None:

    """ """

    hep_name = f'{proceedings_data.event.id}.json'

    async with capacity_limiter:
        hep_file = Path(hep_dir, hep_name)

        if await hep_file.exists():
            await hep_file.unlink()

        # JSON string
        payload = proceedings_data.conference_hep_payload

        # write to file
        await hep_file.write_text(payload)


async def generate_hep_payload_task(capacity_limiter: CapacityLimiter,
                                    contribution_doi: ContributionDOI,
                                    hep_dir: Path) -> None:
    """ """

    async with capacity_limiter:

        hep_file = Path(hep_dir, f'{contribution_doi.code}.json')

        if await hep_file.exists():
            await hep_file.unlink()

        # generate JSON string
        json_text = contribution_doi.as_hep_json()

        # write to a file
        await hep_file.write_text(json_text)
