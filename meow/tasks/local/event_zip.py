import logging as lg


from typing import AsyncGenerator

from meow.services.local.event.event_final_proceedings \
    import event_final_proceedings

from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventZipTask(AbstractTask):
    """ EventZipTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        event: dict = params.get('event', dict())
        cookies: dict = params.get('cookies', dict())
        settings: dict = params.get('settings', dict())

        async for r in event_final_proceedings(event, cookies, settings):
            yield r
