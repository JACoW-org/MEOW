import io
import logging as lg

from anyio import open_file
from anyio import Path
from anyio import run_process
from anyio.streams.file import FileReadStream


logger = lg.getLogger(__name__)


async def compress_final_proceedings(event: dict, cookies: dict, settings: dict) -> None:

    pass
