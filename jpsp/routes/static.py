import logging

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

static = StaticFiles(directory='static')

routes = [
    Mount('/', static, name='static'),
]
