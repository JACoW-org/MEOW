import logging as lg

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


logger = lg.getLogger(__name__)


webui = StaticFiles(directory='webui')

routes = [
    Mount('/', webui, name='webui'),
]
