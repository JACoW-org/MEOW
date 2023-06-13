import logging as lg
from typing import AsyncGenerator
from meow.models.local.event.final_proceedings.proceedings_data_model import FinalProceedingsConfig

from meow.services.local.event.event_final_proceedings import event_final_proceedings
from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventPrePressTask(AbstractTask):
    """EventPrePressTask"""

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        event: dict = params.get("event", dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        indico_session: str = cookies.get("indico_session_http", None)
        cookies["indico_session_http"] = indico_session
        cookies["indico_session"] = indico_session
        
        config = FinalProceedingsConfig(
            strict_pdf_check=False,
            generate_doi_payload=False,
            include_event_slides=False,
            generate_external_doi_url=False,
            include_only_qa_green_contributions=False,
        )
        
        async for r in event_final_proceedings(event, cookies, settings, config):
            self.assert_is_running()
            yield r
