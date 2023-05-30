import logging as lg

from anyio import create_task_group, CapacityLimiter, create_memory_object_stream, open_file, Path

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.tasks.local.doi.models import ContributionDOI

logger = lg.getLogger(__name__)

async def build_doi_payloads(proceedings_data: ProceedingsData) -> ProceedingsData:
    """"""

    logger.info('event_final_proceedings - build_doi_payloads')

    send_stream, receive_stream = create_memory_object_stream()
    capacity_limiter = CapacityLimiter(8)

    # handle directory
    doi_dir = Path('var', 'run', f'{proceedings_data.event.id}_doi')
    await doi_dir.mkdir(exist_ok=True, parents=True)

    async with create_task_group() as tg:
        async with send_stream:
            for contribution in proceedings_data.contributions:
                contribution_doi = contribution.doi_data
                tg.start_soon(generate_doi_payload_task, capacity_limiter, contribution_doi, doi_dir)

    return proceedings_data

async def generate_doi_payload_task(capacity_limiter: CapacityLimiter, contribution_doi: ContributionDOI, doi_dir: Path) -> None:
    """"""

    async with capacity_limiter:

        # generate JSON string
        json_text = contribution_doi.as_json()

        # write to a file
        file_path = Path(doi_dir, contribution_doi.code)
        async with await open_file(file_path, 'w') as json_file:
            await json_file.write(json_text)
