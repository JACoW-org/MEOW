import logging as lg

from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def extract_proceedings_papers(proceedings_data: ProceedingsData) -> list[FileData]:

    files: list[FileData] = []

    for contribution_data in proceedings_data.contributions:
        if contribution_data.is_qa_approved or contribution_data.is_qa_pending:
            if contribution_data.paper and contribution_data.paper.latest_revision:
                revision_data = contribution_data.paper.latest_revision
                for file_data in revision_data.files:
                    if file_data.file_type == FileData.FileType.paper:
                        files.append(file_data)
                    # logger.info(f"{file_data.uuid} - {file_data.filename}")

    return files


async def extract_proceedings_slides(proceedings_data: ProceedingsData) -> list[FileData]:

    files: list[FileData] = []

    for contribution_data in proceedings_data.contributions:
        if contribution_data.slides and contribution_data.slides.latest_revision:
            revision_data = contribution_data.slides.latest_revision
            for file_data in revision_data.files:
                if file_data.file_type == FileData.FileType.slides:
                    files.append(file_data)
                # logger.info(f"{file_data.uuid} - {file_data.filename}")

    return files


async def extract_contributions_papers(proceedings_data: ProceedingsData) -> list[ContributionPaperData]:

    papers: list[ContributionPaperData] = []

    # files: list[FileData] = []

    for contribution_data in proceedings_data.contributions:
        if contribution_data.is_qa_approved or contribution_data.is_qa_pending:
            if contribution_data.paper and contribution_data.paper.latest_revision:
                revision_data = contribution_data.paper.latest_revision
                
                for file_data in revision_data.files:
                    if file_data.file_type == FileData.FileType.paper:
                        papers.append(ContributionPaperData(
                            contribution=contribution_data,
                            paper=file_data
                        ))
                    # logger.info(f"{file_data.uuid} - {file_data.filename}")

    return papers
