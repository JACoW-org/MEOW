import logging as lg

import orjson

from anyio import open_file, create_task_group, CapacityLimiter, Path

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)

from meow.utils.filesystem import rmtree
from meow.tasks.local.reference.models import ContributionRef

logger = lg.getLogger(__name__)


async def build_refs_payloads(proceedings_data: ProceedingsData) -> ProceedingsData:
    """ """

    logger.info("event_final_proceedings - build_refs_payloads")

    refs_name = f"{proceedings_data.event.id}_refs"
    refs_dir = Path("var", "run", f"{refs_name}")
    refs_file = Path(refs_dir, "references.jsonl")

    if await refs_dir.exists():
        await rmtree(str(refs_dir))

    await refs_dir.mkdir(exist_ok=True, parents=True)

    total_contributions: int = len(proceedings_data.contributions)

    logger.info("build_refs_payloads - " + f"contributions: {total_contributions}")

    capacity_limiter = CapacityLimiter(16)

    async with create_task_group() as tg:
        # conference DOI
        tg.start_soon(
            generate_conference_refs_payload_task,
            capacity_limiter,
            proceedings_data,
            refs_dir,
        )

        # contributions DOIs
        for contribution in proceedings_data.contributions:
            if contribution.contribution_ref:
                tg.start_soon(
                    generate_refs_payload_task,
                    capacity_limiter,
                    contribution.contribution_ref,
                    refs_dir,
                )

    await concat_refs_files(proceedings_data, refs_dir, refs_file)

    return proceedings_data


async def concat_refs_files(
    proceedings_data: ProceedingsData, refs_dir: Path, refs_file: Path
):
    refs_event_path = [Path(refs_dir, f"{proceedings_data.event.id}.json")]

    refs_contrib_paths = [
        Path(refs_dir, f"{contribution.contribution_ref.code}.json")
        for contribution in proceedings_data.contributions
        if contribution.contribution_ref
    ]

    hep_paths = refs_event_path + refs_contrib_paths

    async with await open_file(str(refs_file), "a+") as f:
        for p in hep_paths:
            async with await open_file(str(p)) as c:
                json = await c.read()
                await f.write(f"{json}\n")


async def generate_conference_refs_payload_task(
    capacity_limiter: CapacityLimiter, proceedings_data: ProceedingsData, refs_dir: Path
) -> None:
    """ """

    hep_name = f"{proceedings_data.event.id}.json"

    async with capacity_limiter:
        hep_file = Path(refs_dir, hep_name)

        await hep_file.unlink(missing_ok=True)

        # JSON string
        payload = orjson.dumps(proceedings_data.event.as_ref()).decode()

        # write to file
        await hep_file.write_text(payload)


async def generate_refs_payload_task(
    capacity_limiter: CapacityLimiter, contribution_ref: ContributionRef, refs_dir: Path
) -> None:
    """ """

    async with capacity_limiter:
        refs_file = Path(refs_dir, f"{contribution_ref.code}.json")

        await refs_file.unlink(missing_ok=True)

        # generate JSON string
        json_text = orjson.dumps(contribution_ref.as_ref()).decode()

        # write to a file
        await refs_file.write_text(json_text)
