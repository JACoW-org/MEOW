import contextlib

from .shutdown import app_shutdown
from .startup import app_startup


# import anyio
# https://anyio.readthedocs.io/en/stable/tasks.html
# https://www.starlette.io/events/#registering-events
# https://docs.python.org/3/library/contextlib.html


@contextlib.asynccontextmanager
async def run():
    try:
        await app_startup()
        yield
    finally:
        await app_shutdown()
