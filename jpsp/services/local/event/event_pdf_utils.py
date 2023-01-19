

import hashlib as hl

from anyio import Path

async def is_to_download(file: Path, md5: str) -> bool:
    """ """

    already_exists = await file.exists()

    is_to_download = md5 == '' or already_exists == False or md5 != hl.md5(await file.read_bytes()).hexdigest()

    # if is_to_download == True:
    #     print(await file.absolute(), '-->', 'download')
    # else:
    #     print(await file.absolute(), '-->', 'skip')

    return is_to_download
