import io
import logging as lg

from anyio import open_file
from anyio import Path
from anyio import run_process
from anyio.streams.file import FileReadStream


logger = lg.getLogger(__name__)


async def compress_final_proceedings(event: dict, cookies: dict, settings: dict) -> io.BytesIO:

    working_dir = Path(f"/tmp/{event.get('id')}")

    await working_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f'temporary directory {await working_dir.absolute()}')

    mkdocs_yml = Path(working_dir, "mkdocs.yml")

    result = await run_process(f"mkdocs build -f {await mkdocs_yml.absolute()}")

    logger.debug(result.stdout.decode())

    zip_file = Path(working_dir, "out.7z")
    out_dir = Path(working_dir, "out")

    zip_file_path = await zip_file.absolute()
    out_dir_path = await out_dir.absolute()
    
    zip_cmd = await Path('bin', '7zzs').absolute()

    # 7z a /tmp/12/12.7z /tmp/12/out -m0=LZMA2:d=64k -mmt=4
    result = await run_process(f"{zip_cmd} a {zip_file_path} {out_dir_path} -m0=LZMA2:d=64k -mmt=4")
    # result = await run_process(f"zip -6 -r {zip_file_path} {out_dir_path}")

    logger.debug(result.stdout.decode())

    b = io.BytesIO()

    async with await FileReadStream.from_path(zip_file_path) as s:
        async for c in s:
            b.write(c)

    b.seek(0)

    return b
