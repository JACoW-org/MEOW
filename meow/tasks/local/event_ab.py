import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.event_abstract_booklet import event_abstract_booklet

from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventAbTask(AbstractTask):
    """ EventAbTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get('cookies', dict())
        settings: dict = params.get('settings', dict())
        
        async for r in event_abstract_booklet(event, cookies, settings):
            yield r
