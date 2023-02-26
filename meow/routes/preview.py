import logging as lg

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


logger = lg.getLogger(__name__)


preview = StaticFiles(directory='var/html/FEL2022', html=True, check_dir=True)

routes = [
    Mount('/', preview, name='preview'),
]
