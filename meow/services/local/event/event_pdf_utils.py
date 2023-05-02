
import logging as lg
from anyio import Path
from meow.services.local.papers_metadata.pdf_annotations import annot_page_footer, annot_page_header, annot_page_side

from meow.utils.hash import file_md5
from meow.utils.process import run_cmd
from meow.utils.serialization import json_decode, json_encode


logger = lg.getLogger(__name__)


def get_python_cmd():
    return str(Path("venv", "bin", "python3"))


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


async def write_metadata(metadata: dict, read_path: str, write_path: str | None = None) -> int:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'metadata', '-input', read_path]

    if write_path is not None and write_path != '':
        cmd.append(f"-output")
        cmd.append(write_path)

    for key in metadata.keys():
        val = metadata.get(key, None)
        if val is not None and val != '':
            cmd.append(f"-{key}")
            cmd.append(val)

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.returncode

    return 1


async def read_report(read_path: str) -> dict | None:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'report', '-input', read_path]

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return json_decode(res.stdout.decode())

    return None


async def pdf_to_text(read_path: str) -> str:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'text', '-input', read_path]

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.stdout.decode()

    return ''


async def draw_frame(write_path: str, page: int, header: dict | None, footer: dict | None) -> int:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'frame', '-input', write_path]

    cmd.append("-page")
    cmd.append(str(page))

    cmd.append("-header")
    cmd.append(json_encode(header).decode('utf-8'))

    cmd.append("-footer")
    cmd.append(json_encode(footer).decode('utf-8'))

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.returncode

    return 1


async def concat_pdf(write_path: str, files: list[str]) -> int:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'join', '-o', write_path]
    
    res = await run_cmd(cmd + files)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.returncode

    return 1
