"""
Put Event
"""

import anyio
import logging

from typing import Any
from jpsp.services.local.conference.abstract_booklet import create_abstract_booklet_from_entities

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class EventAbTask(AbstractTask):
    """ EventAbTask """

    async def run(self, params: dict) -> Any:
        """ Main Function """

        conference_id: str = params.get("conference_id", "44")
        
        abstract_booklet = await create_abstract_booklet_from_entities(conference_id)
        
        return abstract_booklet
