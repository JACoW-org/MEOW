

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


async def extract_event_pdf_files(event: dict) -> list:
    """ """

    event_files = []

    contributions = await extract_event_contributions(event)

    for contribution in contributions:
        revisions = contribution.get('revisions', [])

        revisions_files = revisions[-1].get('files', []) \
            if revisions is not None and len(revisions) > 0 \
            else []

        event_files.extend(revisions_files)

    return event_files


async def extract_event_contributions(event: dict) -> list[dict]:
    """ """

    return event.get('contributions', [])
