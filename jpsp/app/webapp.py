import uvicorn
import logging as lg

from starlette.applications import Starlette

from jpsp.app.middleware import middleware as app_middleware
from jpsp.app.routes import routes as app_routes

from jpsp.callbacks.shutdown import app_shutdown
from jpsp.callbacks.startup import app_startup

logger = lg.getLogger(__name__)


class UvicornWebappManager:

    async def run(self):

        app = Starlette(
            debug=False,
            routes=app_routes,
            middleware=app_middleware,
            on_startup=[app_startup],
            on_shutdown=[app_shutdown]
        )

        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level='info'
        )

        server = uvicorn.Server(config)

        await server.serve()
