#!/usr/bin/python

import logging as lg

import uvloop

uvloop.install()

from anyio import create_task_group, run

from os import environ
    
environ['CLIENT_TYPE'] = 'webapp'  

from anyio import run
from anyio import create_task_group

lg.basicConfig(level=lg.INFO)
logger = lg.getLogger(__name__)

from jpsp.app.instances.services import srs

# from jpsp.app.state import create_webapp_state, destroy_webapp_state




async def main() -> None:
    logger.debug('jpsp - begin')
    
    import anyio
          
    limiter = anyio.to_thread.current_default_thread_limiter()  # type: ignore 
    limiter.total_tokens = 128

    limiter = anyio.to_process.current_default_process_limiter()  # type: ignore 
    limiter.total_tokens = 64
    
    from nltk import download
    
    download('punkt')
    download('stopwords')
    
    await srs.redis_manager.prepare()
    await srs.redis_manager.migrate()
    await srs.redis_manager.popola()
    
    async with create_task_group() as tg:
        tg.start_soon(srs.webapp_manager.run)
        tg.start_soon(srs.socket_manager.run)    
    
    await srs.redis_manager.destroy()
    
    logger.debug('jpsp - end')




if __name__ == "__main__":
    run(main, backend='asyncio', backend_options={'use_uvloop': True})
    