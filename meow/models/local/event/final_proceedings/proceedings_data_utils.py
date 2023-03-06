import logging as lg

from meow.models.local.event.final_proceedings.contribution_model import FileData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def extract_proceedings_files(proceedings_data: ProceedingsData) -> list[FileData]:

    files: list[FileData] = []

    for contribution_data in proceedings_data.contributions:
        if contribution_data.latest_revision:
            revision_data = contribution_data.latest_revision
            for file_data in revision_data.files:
                files.append(file_data)
                logger.info(f"{file_data.uuid} - {file_data.filename}")

    return files
