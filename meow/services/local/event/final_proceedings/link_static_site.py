import logging as lg

from anyio import Path

from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig, ProceedingsData
from meow.utils.filesystem import rmtree, move


logger = lg.getLogger(__name__)


async def link_static_site(proceedings_data: ProceedingsData, cookies: dict,
                           settings: dict, config: FinalProceedingsConfig) -> ProceedingsData:
    """ """

    static_site_name = f"{proceedings_data.event.id}_src"
    static_site_src = Path('var', 'run', static_site_name)
    static_site_path = Path(static_site_src, 'out')

    site_preview_name = f"{proceedings_data.event.id}"
    site_preview_path = Path('var', 'html', site_preview_name)

    site_archive_name = f"{proceedings_data.event.id}.7z"
    site_archive_path = Path('var', 'html', site_archive_name)

    logger.info(f"{static_site_path} --> {site_preview_path}")

    if await site_archive_path.exists():
        await site_archive_path.unlink()

    await rmtree(str(site_preview_path))
    await move(str(static_site_path), str(site_preview_path))
    await rmtree(str(static_site_src))

    await Path(site_preview_path, config.static_site_type).write_text('')

    return proceedings_data
