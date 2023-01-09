import logging

from typing import AsyncGenerator
from jpsp.services.local.conference.download_pdf import event_pdf_download

from jpsp.tasks.infra.abstract_task import AbstractTask


logger = logging.getLogger(__name__)


class EventPdfTask(AbstractTask):
    """ EventPdfTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        """ Main Function """

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        async for result in event_pdf_download(event, cookies, settings):
            type = result.get('type', '')
            value = result.get('value', None)
            
            yield dict(final=value) \
                if type == 'final' \
                else dict(progress=value)
