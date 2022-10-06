"""
Put Event
"""

import anyio
import logging

from typing import Any
from jpsp.services.local.conference.check_pdf import event_pdf_check

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class CheckPdfTask(AbstractTask):
    """ CheckPdfTask """

    async def run(self, params: dict, context: dict = {}) -> dict:
        """ Main Function """

        check_pdf_input: list[dict] = params.get("contributions", [])
        
        check_pdf_reports = await event_pdf_check(check_pdf_input)
        
        return { 'reports': check_pdf_reports }
