import logging

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

webui = StaticFiles(directory='webui')

routes = [
    Mount('/', webui, name='webui'),
]
