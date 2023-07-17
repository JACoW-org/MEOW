import logging

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount

from meow.routes.api import routes as api_routes
from meow.routes.sse import routes as sse_routes
from meow.routes.socket import routes as socket_routes
from meow.routes.static import routes as static_routes
from meow.routes.preview import routes as preview_routes
from meow.routes.web import routes as web_routes

logger = logging.getLogger(__name__)


async def redirect_endpoint(req: Request):
    return RedirectResponse("/web/index")


routes = [
    # Route('/', endpoint=redirect_endpoint),
    Mount('/web', routes=web_routes),
    Mount("/api", routes=api_routes),
    Mount("/sse", routes=sse_routes),
    Mount("/socket", routes=socket_routes),
    Mount("/static", routes=static_routes),
    Mount("/", routes=preview_routes),
]
