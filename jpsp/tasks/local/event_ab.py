import logging
import base64

from typing import AsyncGenerator

from jpsp.services.local.conference.abstract_booklet \
    import create_abstract_booklet_from_event, \
    export_abstract_booklet_to_odt

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class EventAbTask(AbstractTask):
    """ EventAbTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        """ Main Function """
        
        event = params.get('event', None)
        cookies = params.get('cookies', None)
        settings = params.get('settings', None)

        abstract_booklet = await create_abstract_booklet_from_event(event, cookies, settings)

        abstract_booklet_odt = export_abstract_booklet_to_odt(abstract_booklet, event, cookies, settings)

        b64 = base64.b64encode(abstract_booklet_odt.getvalue()).decode('utf-8')
        
        event_id = params.get('id', 'event')
        event_title = params.get('title', 'title')
        suffix = 'abstrack_booklet'
        ext = 'odt'

        yield {'b64': b64, 'filename': f'{event_id}_{event_title}_{suffix}.{ext}'}
