import logging

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route, Mount

from jpsp.routes.api import routes as api_routes
from jpsp.routes.sse import routes as sse_routes
from jpsp.routes.socket import routes as socket_routes
from jpsp.routes.static import routes as static_routes
from jpsp.routes.webui import routes as webui_routes
from jpsp.routes.web import routes as web_routes

logger = logging.getLogger(__name__)


async def redirect_endpoint(req: Request):
    return RedirectResponse("/web/index")


routes = [
    Route('/', endpoint=redirect_endpoint),
    Mount('/web', routes=web_routes),
    Mount("/api", routes=api_routes),
    Mount("/sse", routes=sse_routes),
    Mount("/socket", routes=socket_routes),
    Mount("/static", routes=static_routes),
    Mount("/webui", routes=webui_routes),
]
