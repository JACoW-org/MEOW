import logging

# from jpsp.app.redis import create_redis_pool

from jpsp.app.state import create_app_state
# from jpsp.app.tasks import create_task_queue

from jpsp.services.local.credential.save_credential import create_default_credentials

logger = logging.getLogger(__name__)


async def app_startup() -> None:
    logger.debug('Starlette startup - BEGIN')

    await create_app_state()
    # await create_redis_pool()
    # await create_task_queue()
    # await create_redis_migrator()
    # await create_socket_manager()
    # await create_worker_manager()
    await create_default_credentials()

    logger.debug('Starlette startup - END')



# async def create_worker_manager() -> None:
#     await srs.workers_manager.subscribe()
    
# async def create_socket_manager() -> None:
#     await srs.ws_manager.subscribe()
