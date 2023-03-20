
import logging as lg
from anyio import Path

from meow.utils.hash import file_md5
from meow.utils.process import run_cmd


logger = lg.getLogger(__name__)


async def is_to_download(file: Path, md5: str) -> bool:
    """ """

    if md5 == '' or not await file.exists():
        return True

    file_path = str(await file.absolute())

    md5_hex = await file_md5(file_path)

    # print(file_path, md5, md5_hex)

    # is_to_download = md5 == '' or already_exists == False or md5 != hl.md5(await file.read_bytes()).hexdigest()

    # if is_to_download == True:
    #     print(await file.absolute(), '-->', 'download')
    # else:
    #     print(await file.absolute(), '-->', 'skip')

    # return is_to_download

    return md5 != md5_hex


async def extract_event_pdf_files(event: dict) -> list:
    """ """

    event_files = []

    for contribution in event.get('contributions', []):
        latest_revision = contribution.get('latest_revision', None)

        revisions_files = latest_revision.get('files', []) \
            if latest_revision is not None \
            else []

        event_files.extend(revisions_files)

    return event_files


async def write_metadata(metadata: dict, read_path: str, write_path: str | None = None) -> None:

    meow_cli_path = str(await Path("meow.py").absolute())
    venv_py_path = str(await Path("venv", "bin", "python3").absolute())

    cmd = [venv_py_path, meow_cli_path, 'metadata', '-input', read_path]

    if write_path is not None and write_path is not '':
        cmd.append(f"-output")
        cmd.append(write_path)

    for key in metadata.keys():
        val = metadata.get(key, None)
        if val is not None and val is not '':
            cmd.append(f"-{key}")
            cmd.append(val)

    await run_cmd(cmd)
