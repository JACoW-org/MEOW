import logging as lg

import os

from anyio import Path, run_process
from anyio import create_memory_object_stream, ClosedResourceError
from anyio.streams.memory import MemoryObjectSendStream

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def link_static_site(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """
    
    static_site_name = f"{proceedings_data.event.id}_hugo_src"
    static_site_dir = await Path('var', 'run', static_site_name, 'out').absolute()
    
    site_preview_name = f"{proceedings_data.event.title}"
    site_preview_dir = await Path('var', 'html', site_preview_name).absolute()
    
    logger.info(f"{static_site_dir} --> {site_preview_dir}")
    
    result = await run_process(['rm', '-rf', f'{site_preview_dir}'])
    logger.info(result.stdout.decode())
    
    result = await run_process(['mv', f'{static_site_dir}', f'{site_preview_dir}'])
    logger.info(result.stdout.decode())
    
    # await static_site_dir.hardlink_to(static_site_dir)
       
    # await site_preview_dir.symlink_to(static_site_dir)
    
    return proceedings_data
