import logging as lg
from typing import Callable

from meow.models.local.event.final_proceedings.contribution_model import ContributionPaperData, FileData
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def extract_proceedings_papers(proceedings_data: ProceedingsData,
                                     callback: Callable) -> list[FileData]:

    papers: list[FileData] = []

    for contribution_data in proceedings_data.contributions:

        # logger.debug(f"""extract_proceedings_papers:
        #             {contribution_data.code} -
        #             {callback(contribution_data)}""")
        #
        # logger.debug(contribution_data.paper)

        if callback(contribution_data) and contribution_data.paper \
                and contribution_data.paper.latest_revision:
            for file_data in contribution_data.paper.latest_revision.files:

                # logger.debug(f"""{file_data.uuid} -
                #             {file_data.filename} -
                #             {file_data.file_type}""")

                if file_data.file_type == FileData.FileType.paper:
                    papers.append(file_data)

    return papers


async def extract_proceedings_slides(proceedings_data: ProceedingsData,
                                     callback: Callable) -> list[FileData]:

    slides: list[FileData] = []

    for contribution_data in proceedings_data.contributions:
        if callback(contribution_data) and contribution_data.slides \
                and contribution_data.slides.latest_revision:
            revision_data = contribution_data.slides.latest_revision
            for file_data in revision_data.files:

                # logger.debug(f"""{file_data.uuid} -
                #             {file_data.filename} -
                #             {file_data.file_type}""")

                if file_data.file_type == FileData.FileType.slides:
                    slides.append(file_data)

    return slides


async def extract_contributions_papers(proceedings_data: ProceedingsData,
                                       callback: Callable) -> list[ContributionPaperData]:

    papers: list[ContributionPaperData] = []

    for contribution_data in proceedings_data.contributions:
        if callback(contribution_data) and contribution_data.paper and contribution_data.paper.latest_revision:
            for file_data in contribution_data.paper.latest_revision.files:

                # logger.debug(f"""{file_data.uuid} -
                #             {file_data.filename} -
                #             {file_data.file_type}""")

                if file_data.file_type == FileData.FileType.paper:
                    papers.append(ContributionPaperData(
                        contribution=contribution_data,
                        paper=file_data
                    ))

    return papers
