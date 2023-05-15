#!/usr/bin/python

from anyio.abc import CancelScope
from anyio import open_signal_receiver
from anyio import create_task_group
from anyio import get_cancelled_exc_class, run
import signal
from os import environ
import logging as lg

import uvloop

# from meow.app.state import create_worker_state, destroy_worker_state

uvloop.install()


environ["CLIENT_TYPE"] = "worker"


# from systemd.journal import JournaldLogHandler

# instantiate the JournaldLogHandler to hook into systemd
# journald_handler = JournaldLogHandler()

# set a formatter to include the level name
# journald_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

# add the journald handler to the current logger
# lg.addHandler(journald_handler)

# optionally set the logging level
# lg.setLevel(logging.DEBUG)


lg.basicConfig(level=lg.INFO)


logger = lg.getLogger(__name__)


async def app_wrap(scope: CancelScope):
    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.warning("SIGINT" if signum == signal.SIGINT else "SIGTERM")
            await app_post()
            scope.cancel()
            return


async def app_pre():

    logger.warning("###################")
    logger.warning("###### PRE ########")
    logger.warning("###################")

    from anyio import to_thread, to_process

    to_thread.current_default_thread_limiter().total_tokens = 8
    to_process.current_default_process_limiter().total_tokens = 8

    from meow.app.instances.services import srs

    await srs.redis_manager.prepare()
    await srs.redis_manager.migrate()
    await srs.redis_manager.popola()
    
    from meow.app.instances.application import app

    app.state.webapp_running = True
    app.state.worker_running = True


async def app_run():
    from meow.app.instances.services import srs
    await srs.workers_manager.run()


async def app_post():

    logger.warning("###################")
    logger.warning("###### POST #######")
    logger.warning("###################")

    from meow.app.instances.services import srs

    await srs.redis_manager.destroy()

    from meow.app.instances.application import app

    app.state.webapp_running = False
    app.state.worker_running = False


async def main() -> None:
    logger.debug("meow - begin")

    try:
        await app_pre()
        
        async with create_task_group() as tg:
            tg.start_soon(app_wrap, tg.cancel_scope)
            tg.start_soon(app_run)

    except BaseException as e:
        logger.error(e, exc_info=True)

    logger.debug("meow - end")


if __name__ == "__main__":
    run(main, backend="asyncio", backend_options={"use_uvloop": True})
