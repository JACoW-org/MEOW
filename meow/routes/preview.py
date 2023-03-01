import logging as lg

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


logger = lg.getLogger(__name__)


preview = StaticFiles(directory='var/html', html=True, check_dir=False)

routes = [
    Mount('/', preview, name='preview'),
]
