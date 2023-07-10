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
    static_site_dir = Path(static_site_src, 'out')

    site_preview_name = f"{proceedings_data.event.id}"
    site_preview_dir = Path('var', 'html', site_preview_name)

    logger.info(f"{static_site_dir} --> {site_preview_dir}")

    await rmtree(str(site_preview_dir))
    await move(str(static_site_dir), str(site_preview_dir))
    await rmtree(str(static_site_src))

    await Path(site_preview_dir, config.static_site_type).write_text('')

    return proceedings_data
