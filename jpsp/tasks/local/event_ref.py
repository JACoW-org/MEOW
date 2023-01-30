import logging as lg

from typing import AsyncGenerator

from jpsp.services.local.event.event_contribution_reference \
    import event_contribution_reference

from jpsp.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventRefTask(AbstractTask):
    """ EventRefTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())
        
        async for r in event_contribution_reference(event, cookies, settings):
            yield r