import logging

from jpsp.app.redis import create_redis_pool, create_redis_migrator

from jpsp.app.state import create_app_state
from jpsp.app.tasks import create_task_queue

from jpsp.services.local.settings.save_settings import create_default_settings

logger = logging.getLogger(__name__)


from jpsp.app.instances.services import srs


async def app_startup():
    logger.debug('Starlette startup - BEGIN')

    #from main import app

    await create_app_state()
    await create_redis_pool()
    await create_task_queue()
    await create_redis_migrator()
    await create_socket_manager()
    await create_worker_manager()
    await create_default_settings()

    # await create_signal_handler()

    logger.debug('Starlette startup - END')

    #return app


async def create_worker_manager():
    await srs.workers_manager.subscribe()
    
async def create_socket_manager():
    await srs.ws_manager.subscribe()
