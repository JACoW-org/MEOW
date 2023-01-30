import logging

from jpsp.app.instances.application import app

logger = logging.getLogger(__name__)


async def create_webapp_state():
    """ """

    logger.debug('create_app_state >>>')

    app.state.webapp_running = True


async def destroy_webapp_state():
    """ """

    logger.debug('destroy_app_state >>>')

    app.state.webapp_running = False



async def create_worker_state():
    """ """

    logger.debug('create_worker >>>')

    app.state.worker_running = True


async def destroy_worker_state():
    """ """

    logger.debug('destroy_worker_state >>>')

    app.state.worker_running = False