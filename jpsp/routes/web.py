import logging as lg

from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

logger = lg.getLogger(__name__)

jinja = Jinja2Templates(directory='jinja')


async def index_endpoint(request: Request) -> Response:
    return jinja.TemplateResponse('index.html.jinja', {'request': request})


async def conferences_endpoint(request: Request) -> Response:
    return jinja.TemplateResponse('conferences.html.jinja', {'request': request})


routes = [
    Route('/index', index_endpoint, methods=['GET']),
    Route('/conferences', conferences_endpoint, methods=['GET']),
]
