#!/usr/bin/python

import logging as lg

import uvloop
uvloop.install()

from anyio import create_task_group, run

from os import environ

environ['CLIENT_TYPE'] = 'worker'


lg.basicConfig(level=lg.INFO)
logger = lg.getLogger(__name__)


from meow.app.instances.services import srs



async def main() -> None:
    logger.debug('meow - begin')
    
    from anyio import to_thread, to_process
          
    to_thread.current_default_thread_limiter().total_tokens = 4
    to_process.current_default_process_limiter().total_tokens = 4
    
    from nltk import download
    
    download('punkt')
    download('stopwords')

    await srs.redis_manager.prepare()
    await srs.redis_manager.migrate()
    await srs.redis_manager.popola()

    async with create_task_group() as tg:
        tg.start_soon(srs.webapp_manager.run)
        tg.start_soon(srs.socket_manager.run)
        tg.start_soon(srs.workers_manager.run)

    await srs.redis_manager.destroy()

    logger.debug('meow - end')


if __name__ == "__main__":
    run(main, backend='asyncio', backend_options={'use_uvloop': True})


# if __name__ == "__main__":
#
#     app = Starlette(
#         debug=False,
#         routes=app_routes,
#         middleware=app_middleware,
#         on_startup=[app_startup],
#         on_shutdown=[app_shutdown]
#     )
#
#     uvicorn.run(
#         app=app,
#         host="127.0.0.1",
#         port=8000,
#         log_level='info',
#         workers=2
#     )
#
#
#
# async def webapp():
#     logger.info('webapp >>>')
#
#     app = Starlette(
#         debug=False,
#         routes=app_routes,
#         middleware=app_middleware,
#         on_startup=[app_startup],
#         on_shutdown=[app_shutdown]
#     )
#
#     uvicorn.run(app, host="127.0.0.1", port=8000, log_level='info', workers=1)
#
#
# async def worker():
#     logger.info('worker >>>')
#     await sleep(1)
#
#
# async def main():
#     async with create_task_group() as tg:
#         tg.start_soon(webapp)
#         tg.start_soon(worker)
#
#     print('All tasks finished!')
#
#
# run(main)
# 
# 
# async def app(scope, receive, send):
#
#     app = Starlette(
#         debug=False,
#         routes=app_routes,
#         middleware=app_middleware,
#         on_startup=[app_startup],
#         on_shutdown=[app_shutdown]
#     )
#
#     return app
