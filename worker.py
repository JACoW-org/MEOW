#!/usr/bin/python

import logging as lg

import uvloop

# from jpsp.app.state import create_worker_state, destroy_worker_state

uvloop.install()

from os import environ

environ['CLIENT_TYPE'] = 'worker'

import signal


from anyio import run
from anyio import create_task_group
from anyio import open_signal_receiver
from anyio.abc import CancelScope


lg.basicConfig(level=lg.INFO)
logger = lg.getLogger(__name__)


from jpsp.app.instances.services import srs



async def signal_handler(scope: CancelScope):
    
    from jpsp.app.instances.application import app    
    app.state.webapp_running = True
    app.state.worker_running = True
    
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.info('SIGINT' if signum == signal.SIGINT else 'SIGTERM')
            scope.cancel()
            app.state.webapp_running = False
            app.state.worker_running = False
            return
            
    

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
        tg.start_soon(signal_handler, tg.cancel_scope)
        tg.start_soon(srs.workers_manager.run)
        
    await srs.redis_manager.destroy()

    logger.debug('jpsp - end')


if __name__ == "__main__":    
    run(main, backend='asyncio', backend_options={'use_uvloop': True})
    