import logging
import shutil

from anyio import to_thread as to


logger = logging.getLogger(__name__)


async def cptree(src_dir: str, dst_dir: str):

    def _cptree(src: str, dst: str):
        shutil.copytree(src, dst)

    await to.run_sync(_cptree, src_dir, dst_dir)


async def rmtree(src_dir: str):

    def _rmtree(src_dir: str):
        shutil.rmtree(src_dir, ignore_errors=True)

    await to.run_sync(_rmtree, src_dir)


async def move(src_dir: str, dst_dir: str):

    def _move(src_dir: str, dst_dir: str):
        shutil.move(src_dir, dst_dir)

    await to.run_sync(_move, src_dir, dst_dir)
