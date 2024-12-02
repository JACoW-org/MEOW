#!/usr/bin/python

from anyio import run
from anyio import create_task_group
from anyio import open_signal_receiver
from anyio.abc import CancelScope

import logging as lg
import os

import nltk
nltk.download()

os.environ["CLIENT_TYPE"] = "worker"

lg.basicConfig(level=lg.INFO)

logger = lg.getLogger(__name__)


async def app_wrap(scope: CancelScope):
    import signal

    with open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for signum in signals:
            logger.warning("SIGINT" if signum == signal.SIGINT else "SIGTERM")
            await app_post()
            scope.cancel()
            return


async def app_pre():
    from meow.app.instances.application import app
    app.state.worker_running = True


async def app_run():
    from meow.app.instances.services import srs
    await srs.workers_manager.run()


async def app_post():
    from meow.app.instances.services import srs
    await srs.redis_manager.destroy()

    from meow.app.instances.application import app
    app.state.worker_running = False


async def main() -> None:

    logger.info(f"Started worker process [{os.getpid()}]")

    try:
        await app_pre()

        async with create_task_group() as tg:
            with CancelScope():
                tg.start_soon(app_wrap, tg.cancel_scope)
                tg.start_soon(app_run)

    except BaseException as e:
        logger.error(e, exc_info=True)


if __name__ == "__main__":
    run(main, backend="asyncio", backend_options={"use_uvloop": True})
