import logging

logger = logging.getLogger(__name__)


async def app_startup() -> None:
    logger.debug('Starlette startup - BEGIN')

    from asyncio import create_task
    from meow.callbacks.tasks import add

    async def _start_task() -> None:
        from meow.app.instances.application import app
        app.state.webapp_running = True

    await _start_task()

    # async def _redis_task() -> None:
    #     from meow.app.instances.services import srs
    #     await srs.redis_manager.prepare()
    #     await srs.redis_manager.migrate()
    #     await srs.redis_manager.popola()
    #
    # await _redis_task()

    # add(create_task(_redis_task()))

    async def _socket_task() -> None:
        from meow.app.instances.services import srs
        await srs.socket_manager.run()

    add(create_task(_socket_task()))

    logger.debug('Starlette startup - END')
