"""
Put Event
"""

import logging

from typing import  AsyncGenerator
from jpsp.services.local.conference.check_pdf import event_pdf_check

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class CheckPdfTask(AbstractTask):
    """ CheckPdfTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        """ Main Function """

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        async for progress in event_pdf_check(event, cookies, settings):
            yield {'progress': progress}
