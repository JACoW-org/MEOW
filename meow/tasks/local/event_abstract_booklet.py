import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.event_abstract_booklet import event_abstract_booklet

from meow.tasks.infra.abstract_task import AbstractTask


logger = lg.getLogger(__name__)


class EventAbstractBookletTask(AbstractTask):
    """ EventAbstractBookletTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:

        event: dict = params.get('event', dict())
        cookies: dict = params.get('cookies', dict())
        settings: dict = params.get('settings', dict())

        indico_session: str = cookies.get('indico_session_http', None)
        cookies['indico_session_http'] = indico_session
        cookies['indico_session'] = indico_session

        async for r in event_abstract_booklet(event, cookies, settings):
            self.assert_is_running()
            yield r
