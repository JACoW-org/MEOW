
import logging as lg

import os
import shutil

from anyio import run, Path

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def main():
    """ """
    
    static_site_name = "12_hugo_src"
    static_site_dir = await Path('var', 'run', static_site_name, 'out').absolute()
    
    site_preview_name = "FEL2022"
    site_preview_dir = await Path('var', 'html', site_preview_name).absolute()
    
    logger.info(f"{site_preview_dir} --> {static_site_dir}")
    
    os.link(static_site_dir, site_preview_dir)
    
    # await static_site_dir.hardlink_to(static_site_dir)
       
    # await site_preview_dir.symlink_to(static_site_dir)
    


if __name__ == '__main__':
    run(main)
