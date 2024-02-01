import logging
from anyio import sleep


logger = logging.getLogger(__name__)


async def app_shutdown():
    logger.info('Starlette shutdown - BEGIN')

    async def _stop_task() -> None:
        from meow.app.instances.application import app
        app.state.webapp_running = False

    await _stop_task()

    await sleep(.5)

    async def _redis_task() -> None:
        from meow.app.instances.services import srs
        await srs.redis_manager.destroy()

    await _redis_task()

    from meow.callbacks.tasks import close_all
    await close_all()

    logger.debug('Starlette shutdown - END')
