"""
Put Event
"""

import anyio
import logging

from typing import Any, AsyncGenerator
from jpsp.services.local.conference.check_pdf import event_pdf_check

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class CheckPdfTask(AbstractTask):
    """ CheckPdfTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        """ Main Function """

        check_pdf_input: list[dict] = params.get("contributions", [])

        async for progress in event_pdf_check(check_pdf_input):
            yield {'progress': progress}
