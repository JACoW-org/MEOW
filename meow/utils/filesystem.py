import logging
import shutil

from anyio import to_thread as to


logger = logging.getLogger(__name__)


def _rmtree(src_dir: str):
    shutil.rmtree(src_dir, ignore_errors=True)


async def rmtree(src_dir: str):
    await to.run_sync(_rmtree, src_dir)


def _move(src_dir: str, dst_dir: str):
    shutil.move(src_dir, dst_dir)


async def move(src_dir: str, dst_dir: str):
    await to.run_sync(_move, src_dir, dst_dir)
