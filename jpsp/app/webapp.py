import logging as lg
    
from starlette.applications import Starlette

from jpsp.app.middleware import middleware as app_middleware
from jpsp.app.routes import routes as app_routes
from jpsp.app.config import conf

from jpsp.callbacks.shutdown import app_shutdown
from jpsp.callbacks.startup import app_startup

logger = lg.getLogger(__name__)


def _get_app():
    return Starlette(
        debug=False,
        routes=app_routes,
        middleware=app_middleware,
        on_startup=[app_startup],
        on_shutdown=[app_shutdown]
    )


async def run_unicorn(app):
    import uvicorn

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=conf.SERVER_PORT,
        log_level=conf.LOG_LEVEL
    )

    await uvicorn.Server(config).serve()
    

async def run_hypercorn(app):
    from hypercorn.config import Config
    from hypercorn.asyncio import serve
    
    SECONDS = 1.0
    
    config = Config()
    config.bind = [f"0.0.0.0:8443"]
    config.certfile = "ssl/cert.crt"
    config.keyfile = "ssl/cert.key"
    config.loglevel = "debug"
    config.insecure_bind = [f"0.0.0.0:{conf.SERVER_PORT}"]
    config.startup_timeout = 60 * SECONDS
    config.graceful_timeout = 3 * SECONDS
    config.shutdown_timeout = 30 * SECONDS
    
    await serve(app, config)



class UvicornWebappManager:

    async def run(self):

        app = _get_app()

        await run_unicorn(app)
        # await run_hypercorn(app)
