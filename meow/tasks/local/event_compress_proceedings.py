import logging as lg


from typing import AsyncGenerator

from meow.services.local.event.event_compress_proceedings import event_compress_proceedings

from meow.tasks.infra.abstract_task import AbstractTask
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsTask


logger = lg.getLogger(__name__)


class EventCompressProceedingsTask(AbstractTask):
    """EventCompressProceedingsTask"""

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        event: dict = params.get("event", dict())
        cookies: dict = params.get("cookies", dict())
        settings: dict = params.get("settings", dict())

        indico_session: str = cookies.get("indico_session_http", None)
        cookies["indico_session_http"] = indico_session
        cookies["indico_session"] = indico_session

        tasks = [
            ProceedingsTask(code='adapting_final_proceedings',
                                 text='Adapting final proceedings'),
            ProceedingsTask(code='compress_static_site',
                                 text='Compress Static site')
        ]

        yield dict(type='progress', value=dict(
            phase='init_tasks_list',
            tasks=tasks
        ))

        async for r in event_compress_proceedings(event, cookies, settings):
            self.assert_is_running()
            yield r
