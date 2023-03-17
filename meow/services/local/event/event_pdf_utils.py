
import logging as lg
from anyio import Path

from meow.utils.hash import file_md5


logger = lg.getLogger(__name__)


async def is_to_download(file: Path, md5: str) -> bool:
    """ """
    
    if md5 == '' or not await file.exists(): return True
  
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

