from starlette.applications import Starlette

from jpsp.app.routes import routes as app_routes
from jpsp.app.middleware import middleware as app_middleware

from jpsp.callbacks.shutdown import app_shutdown
from jpsp.callbacks.startup import app_startup

from jpsp.app.instances.services import srs

async def app_pre() -> None:
    await srs.redis_manager.prepare()
    await srs.redis_manager.migrate()
    
async def app_post() -> None:
    await srs.redis_manager.destroy()
    
app = Starlette(
    debug=False,
    routes=app_routes,
    middleware=app_middleware,
    on_startup=[app_pre, app_startup],
    on_shutdown=[app_shutdown, app_post]
)
