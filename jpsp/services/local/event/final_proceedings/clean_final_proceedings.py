import logging as lg

from anyio import Path


logger = lg.getLogger(__name__)


async def clean_final_proceedings(event: dict, cookies: dict, settings: dict):
    
    working_dir = Path(f"/tmp/{event.get('id')}")
    
    await working_dir.mkdir(parents=True, exist_ok=True)

    logger.debug('temporary directory', await working_dir.absolute())
    
    # await working_dir.rmdir()
    
    