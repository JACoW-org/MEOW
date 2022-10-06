"""
Event AB
"""

import logging
import io
import base64

from typing import Any

from jpsp.services.local.conference.abstract_booklet \
    import create_abstract_booklet_from_event, \
    export_abstract_booklet_to_odt

from jpsp.tasks.infra.abstract_task import AbstractTask

logger = logging.getLogger(__name__)


class EventAbTask(AbstractTask):
    """ EventAbTask """

    async def run(self, params: dict, context: dict = {}) -> dict:
        """ Main Function """

        abstract_booklet = await create_abstract_booklet_from_event(params)

        abstract_booklet_odt = export_abstract_booklet_to_odt(abstract_booklet)

        b64 = base64.b64encode(abstract_booklet_odt.getvalue()).decode('utf-8')
        
        event_id = params.get('id', '')
        event_title = params.get('title', '')
        
        filename = f'{event_id}_{event_title}_abstrack_booklet.odt'

        return {'b64': b64, 'filename': filename}
