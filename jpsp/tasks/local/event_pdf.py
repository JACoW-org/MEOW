import logging as lg

from typing import AsyncGenerator
from jpsp.services.local.event.event_pdf_keywords import event_pdf_keywords

from jpsp.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventPdfTask(AbstractTask):
    """ EventPdfTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())
        
        async for r in event_pdf_keywords(event, cookies, settings):
            yield r