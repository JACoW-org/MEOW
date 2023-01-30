import logging

# from jpsp.app.redis import destroy_redis_pool
from jpsp.app.state import destroy_webapp_state, destroy_worker_state

from jpsp.models.infra.locks import RedisLockList
from jpsp.utils.http import HttpClientSessions


logger = logging.getLogger(__name__)


async def app_shutdown():
    logger.debug('Starlette shutdown - BEGIN')

    #from main import app

    await destroy_webapp_state()
    # await destroy_worker_state()

    await HttpClientSessions.close_client_sessions()
    await RedisLockList.release_all_locks()

    # await destroy_socket_manager()
    # await destroy_worker_manager()

    # await destroy_redis_pool()

    logger.debug('Starlette shutdown - END')




# async def destroy_worker_manager():
#     await srs.workers_manager.unsubscribe()

# async def destroy_socket_manager():
#     await srs.ws_manager.unsubscribe()
