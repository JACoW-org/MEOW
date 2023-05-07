import logging as lg

from typing import AsyncGenerator
from meow.services.local.event.event_pdf_keywords import event_pdf_keywords

from meow.tasks.infra.abstract_task import AbstractTask
from meow.tasks.local.reference import ContribRef


logger = lg.getLogger(__name__)


class EventPdfTask(AbstractTask):
    """ EventPdfTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())
        
        indico_session: str = cookies.get('indico_session_http', None)
        cookies['indico_session_http'] = indico_session
        cookies['indico_session'] = indico_session
        
        async for r in event_pdf_keywords(event, cookies, settings):
            yield r