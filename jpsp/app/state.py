import logging

from jpsp.app.instances.application import app

logger = logging.getLogger(__name__)


async def create_app_state():
    """ """

    logger.debug('create_app_state >>>')

    app.state.running = True


async def destroy_app_state():
    """ """

    logger.debug('destroy_app_state >>>')

    app.state.running = False
