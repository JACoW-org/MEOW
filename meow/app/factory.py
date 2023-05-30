""" """
from starlette.applications import Starlette

def build() -> Starlette:
    """ """
       
    from meow.app.middleware import middleware as app_middleware
    from meow.app.routes import routes as app_routes
    from meow.callbacks.shutdown import app_shutdown
    from meow.callbacks.startup import app_startup

    return Starlette(
        debug=False,
        routes=app_routes,
        middleware=app_middleware,
        on_startup=[app_startup],
        on_shutdown=[app_shutdown]
    )

# logger = lg.getLogger(__name__)


# from meow.app.config import conf
#
# async def run_unicorn(app):
#     import uvicorn
#
#     config = uvicorn.Config(
#         app=app,
#         host="0.0.0.0",
#         port=conf.SERVER_PORT,
#         log_level=conf.LOG_LEVEL,
#     )
#
#     server = uvicorn.Server(config)
#
#     # original_handler = uvicorn.Server.handle_exit
#     #
#     # from meow.app.instances.application import app
#     #
#     # app.state.webapp_running = True
#     # app.state.worker_running = True
#     #
#     # def handle_exit(*args, **kwargs):
#     #     """ """
#     #
#     #     app.state.webapp_running = False
#     #     app.state.worker_running = False
#     #
#     #     original_handler(*args, **kwargs)
#     #
#     # uvicorn.Server.handle_exit = handle_exit
#
#     await server.serve()
#
#
# class UvicornWebappManager:
#
#     async def run(self):
#
#         app = build()
#
#         await run_unicorn(app)
