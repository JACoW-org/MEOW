import logging
import base64

from typing import AsyncGenerator

from jpsp.services.local.final_proceedings.create_final_proceedings \
    import create_final_proceedings

from jpsp.services.local.final_proceedings.generate_final_proceedings \
    import generate_final_proceedings
    
from jpsp.services.local.final_proceedings.compress_final_proceedings \
    import compress_final_proceedings
    
from jpsp.services.local.final_proceedings.clean_final_proceedings \
    import clean_final_proceedings

from jpsp.tasks.infra.abstract_task import AbstractTask


logger = logging.getLogger(__name__)


class EventZipTask(AbstractTask):
    """ EventZipTask """

    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator[dict, None]:
        """ Main Function """
        
        event: dict = params.get('event', dict())
        cookies: dict = params.get('cookies', dict())
        settings: dict = params.get('settings', dict())

        final_proceedings = await create_final_proceedings(event, cookies, settings)
        
        await generate_final_proceedings(final_proceedings)

        zip = await compress_final_proceedings(event, cookies, settings)
        
        await clean_final_proceedings(event, cookies, settings)

        b64 = base64.b64encode(zip.getvalue()).decode('utf-8')
        
        event_id = params.get('id', 'event')
        event_title = params.get('title', 'title')
        suffix = 'final_proceedings'
        ext = '7z'

        yield {'b64': b64, 'filename': f'{event_id}_{event_title}_{suffix}.{ext}'}
