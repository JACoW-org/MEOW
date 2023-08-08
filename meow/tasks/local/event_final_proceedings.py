import logging as lg


from typing import AsyncGenerator
from meow.models.local.event.final_proceedings.proceedings_data_model import (
    FinalProceedingsConfig, FinalProceedingsTask)

from meow.services.local.event.event_final_proceedings import event_final_proceedings

from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventFinalProceedingsTask(AbstractTask):
    """EventFinalProceedingsTask"""

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        event: dict = params.get("event", dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        indico_session: str = cookies.get("indico_session_http", None)
        cookies["indico_session_http"] = indico_session
        cookies["indico_session"] = indico_session

        config = FinalProceedingsConfig(
            strict_pdf_check=False,
            include_event_slides=True,
            generate_doi_payload=True,
            generate_external_doi_url=True,
            include_only_qa_green_contributions=True,
            absolute_pdf_link=True,
            static_site_type='proceedings'
        )

        tasks: list[FinalProceedingsTask] = [
            FinalProceedingsTask(code='collecting_sessions_and_attachments',
                                 text='Collecting sessions and attachments'),
            FinalProceedingsTask(code='collecting_contributions_and_files',
                                 text='Collecting contributions and files'),
            FinalProceedingsTask(code='adapting_final_proceedings',
                                 text='Adapting final proceedings'),
            FinalProceedingsTask(code='clean_static_site',
                                 text='Clean Static site'),
            FinalProceedingsTask(code='download_event_attachments',
                                 text='Download event attachments'),
            FinalProceedingsTask(code='download_contributions_papers',
                                 text='Download Contributions Papers'),
            FinalProceedingsTask(code='download_contributions_slides',
                                 text='Download Contributions Slides'),
            FinalProceedingsTask(code='read_papers_metadata',
                                 text='Read Papers Metadata'),
            FinalProceedingsTask(code='validate_contributions_papers',
                                 text='Validate Contributions Papers'),
            FinalProceedingsTask(code='extract_contribution_references',
                                 text='Extract Contribution References'),
            FinalProceedingsTask(code='generate_contribution_doi',
                                 text='Generate Contribution DOI'),
            FinalProceedingsTask(code='generate_doi_payloads',
                                 text='Generate DOI payloads'),
            FinalProceedingsTask(code='manage_duplicates',
                                 text='Managing duplicates'),
            FinalProceedingsTask(code='write_papers_metadata',
                                 text='Write Papers Metadata'),
            FinalProceedingsTask(code='generate_contributions_groups',
                                 text='Generate Contributions Groups'),
            FinalProceedingsTask(code='concat_contribution_papers',
                                 text='Concat Contributions Papers'),
            FinalProceedingsTask(code='generate_site_pages',
                                 text='Generate Site Pages'),
            FinalProceedingsTask(code='copy_event_pdf',
                                 text='Copy event PDF'),
            FinalProceedingsTask(code='clean_static_site_2',
                                 text='Clean Static site'),
            FinalProceedingsTask(code='generate_final_proceedings',
                                 text='Generate Final Proceedings'),
            FinalProceedingsTask(code='link_static_site',
                                 text='Link Static site')
        ]

        yield dict(type='progress', value=dict(
            phase='init_tasks_list',
            tasks=tasks
        ))

        async for r in event_final_proceedings(event, cookies, settings, config):
            self.assert_is_running()
            yield r
