

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


async def extract_proceedings_files(proceedings_data: ProceedingsData) -> list[FileData]:

    files: list[FileData] = []
    
    for contribution_data in proceedings_data.contributions:
        for revision_data in contribution_data.revisions:
            for file_data in revision_data.files:
                files.append(file_data)
                
    return files
