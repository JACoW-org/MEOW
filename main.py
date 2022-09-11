import uvicorn
import logging as lg

from starlette.applications import Starlette

from jpsp.app.middleware import middleware as app_middleware
from jpsp.app.routes import routes as app_routes

from jpsp.callbacks.shutdown import app_shutdown
from jpsp.callbacks.startup import app_startup

from anyio import sleep, create_task_group, run


lg.basicConfig(level=lg.INFO)
logger = lg.getLogger(__name__)


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



if __name__ == "__main__":
    
    app = Starlette(
        debug=False,
        routes=app_routes,
        middleware=app_middleware,
        on_startup=[app_startup],
        on_shutdown=[app_shutdown]
    )
    
    uvicorn.run(
        app=app, 
        host="127.0.0.1",
        port=8000,
        log_level='info',
        workers=1
    )
