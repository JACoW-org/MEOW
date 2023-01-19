import logging as lg

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


logger = lg.getLogger(__name__)


static = StaticFiles(directory='static')

routes = [
    Mount('/', static, name='static'),
]
