import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.event_contribution_reference \
    import event_contribution_reference

from meow.tasks.infra.abstract_task import AbstractTask

from meow.services.local.event.event_contribution_doi import event_contribution_doi


logger = lg.getLogger(__name__)


class EventRefTask(AbstractTask):
    """ EventRefTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())
        
        # async for r in event_contribution_reference(event, cookies, settings):
        #     yield r

        async for r in event_contribution_doi(event, cookies, settings):
            yield r