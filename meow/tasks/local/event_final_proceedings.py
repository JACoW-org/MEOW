""" Module responsible to configure the final proceedings generation """

import logging as lg

from typing import AsyncGenerator

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsConfig, ProceedingsTask)
from meow.services.local.event.event_proceedings import event_proceedings
from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventFinalProceedingsTask(AbstractTask):
    """EventFinalProceedingsTask"""

    async def run(self, params: dict, context: dict | None = None) -> AsyncGenerator[dict, None]:
        event: dict = params.get("event", dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        indico_session: str = cookies.get("indico_session_http", None)
        cookies["indico_session_http"] = indico_session
        cookies["indico_session"] = indico_session

        config = ProceedingsConfig(
            strict_pdf_check=False,
            include_event_slides=True,
            generate_doi_payload=True,
            generate_external_doi_url=True,
            generate_hep_payload=True,
            include_only_qa_green_contributions=True,
            absolute_pdf_link=True,
            static_site_type='proceedings'
        )

        tasks: list[ProceedingsTask] = [
            ProceedingsTask(code='collecting_sessions_and_materials',
                            text='Collecting Sessions and Materials'),
            ProceedingsTask(code='collecting_contributions_and_files',
                            text='Collecting Contributions and Files'),
            ProceedingsTask(code='adapting_proceedings',
                            text='Adapting Final Proceedings'),
            ProceedingsTask(code='clean_static_site',
                            text='Clean Static Site'),
            ProceedingsTask(code='download_event_materials',
                            text='Download Event Materials'),
            ProceedingsTask(code='download_contributions_papers',
                            text='Download Contributions Papers'),
            ProceedingsTask(code='download_contributions_slides',
                            text='Download Contributions Slides'),
            ProceedingsTask(code='read_papers_metadata',
                            text='Read Papers Metadata'),
            ProceedingsTask(code='validate_contributions_papers',
                            text='Validate Contributions Papers'),
            ProceedingsTask(code='extract_contribution_references',
                            text='Extract Contribution References'),
            ProceedingsTask(code='manage_duplicates',
                            text='Managing Duplicates'),
            ProceedingsTask(code='generate_dois',
                            text='Generate DOIs'),
            ProceedingsTask(code='write_papers_metadata',
                            text='Write Papers Metadata'),
            ProceedingsTask(code='generate_contributions_groups',
                            text='Generate Contributions Groups'),
            ProceedingsTask(code='concat_contribution_papers',
                            text='Concat Contributions Papers'),
            ProceedingsTask(code='generate_doi_payloads',
                            text='Generate DOI payloads'),
            ProceedingsTask(code='generate_inspirehep_payloads',
                            text='Generate Inspirehep payloads'),
            ProceedingsTask(code='generate_site_pages',
                            text='Generate Site Pages'),
            ProceedingsTask(code='copy_event_pdf',
                            text='Copy Event PDF'),
            ProceedingsTask(code='generate_proceedings',
                            text='Generate Final Proceedings'),
            ProceedingsTask(code='link_static_site',
                            text='Link Static site')
        ]

        yield dict(type='progress', value=dict(
            phase='init_tasks_list',
            tasks=tasks
        ))

        async for r in event_proceedings(event, cookies, settings, config):
            self.assert_is_running()
            yield r
