import logging as lg

from anyio import Path, run_process

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.utils.filesystem import rmtree, move


logger = lg.getLogger(__name__)


async def compress_static_site(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """
    
    if proceedings_data.event.path and len(proceedings_data.event.path.strip()) > 0:
    
        # static_site_name = f"{proceedings_data.event.id}_hugo_src"
        # static_site_dir = await Path('var', 'run', static_site_name, 'out').absolute()
        # static_site_zip = await Path('var', 'run', static_site_name, 'out.7z').absolute()
        # 
        # site_preview_name = f"{proceedings_data.event.path}"
        # site_preview_dir = await Path('var', 'html', site_preview_name).absolute()
        # site_preview_zip = await Path('var', 'html', f"{site_preview_name}.7z").absolute()
        # 
        # logger.info(f"{static_site_dir} --> {site_preview_dir}")
        #     
        # await rmtree(str(site_preview_dir))
        # 
        # await move(str(static_site_dir), str(site_preview_dir))
        # await move(str(static_site_zip), str(site_preview_zip))
        
        
        zip_cmd = Path('bin', '7zzs')
        
        static_site_name = f"{proceedings_data.event.id}_hugo_src"
        static_site_dir = await Path('var', 'run', static_site_name, 'out').absolute()
        static_site_zip = await Path('var', 'run', static_site_name, 'out.7z').absolute()
        
        site_preview_name = f"{proceedings_data.event.path}"
        site_preview_dir = await Path('var', 'html', site_preview_name).absolute()
        site_preview_zip = await Path('var', 'html', f"{site_preview_name}.7z").absolute()
        
        logger.info(f"{static_site_dir} --> {site_preview_dir}")
            
        await rmtree(str(site_preview_zip))
        
        zip_args = [f"{zip_cmd}", "a",
            "-t7z", "-m0=Deflate",
            "-ms=16m", "-mmt=4", "-mx=1", "--",
            f"{site_preview_zip}", f"{site_preview_dir}"]
        
        logger.info(zip_args)

        result = await run_process(zip_args)
        
        logger.info(result.stdout.decode())
        logger.info(result.stderr.decode())

        if result.returncode == 0:
            logger.info(result.stdout.decode())
        else:
            logger.info(result.stderr.decode())
        
        
        
    else:
        
        logger.warning(f"invalid event.path")
    
    # result = await run_process(['rm', '-rf', f'{site_preview_dir}'])
    # logger.info(result.stdout.decode())
    # shutil.rmtree(site_preview_dir, ignore_errors=True)
    # result = await run_process(['mv', f'{static_site_dir}', f'{site_preview_dir}'])
    # logger.info(result.stdout.decode())
    
    # await static_site_dir.hardlink_to(static_site_dir)
    # await site_preview_dir.symlink_to(static_site_dir)
    
    return proceedings_data

