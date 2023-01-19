import logging as lg

import uvloop
uvloop.install()

from anyio import create_task_group, run

from jpsp.app.instances.services import srs


lg.basicConfig(level=lg.INFO)
logger = lg.getLogger(__name__)


async def jpsp_worker():
    # logger.info('jpsp_worker - begin')

    await srs.workers_manager.run()

    # logger.info('jpsp_worker - end')


async def jpsp_webapp() -> None:
    # logger.info('jpsp_webapp - begin')

    await srs.webapp_manager.run()

    # logger.info('jpsp_webapp - end')


async def jpsp_socket() -> None:
    # logger.info('jpsp_webapp - begin')

    await srs.socket_manager.run()

    # logger.info('jpsp_webapp - end')


async def main() -> None:
    # logger.info('jpsp - begin')
    
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

    async with create_task_group() as tg:
        tg.start_soon(jpsp_webapp)
        tg.start_soon(jpsp_worker)
        tg.start_soon(jpsp_socket)

    await srs.redis_manager.destroy()

    # logger.info('jpsp - end')


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
