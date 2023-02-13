import base64
import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.final_proceedings.create_final_proceedings \
    import create_final_proceedings

from meow.services.local.event.final_proceedings.generate_final_proceedings \
    import generate_final_proceedings

from meow.services.local.event.final_proceedings.compress_final_proceedings \
    import compress_final_proceedings

from meow.services.local.event.final_proceedings.clean_final_proceedings \
    import clean_final_proceedings
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import HugoFinalProceedingsPlugin


logger = lg.getLogger(__name__)


async def event_final_proceedings(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    fp = await create_final_proceedings(event, cookies, settings)

    plugin = HugoFinalProceedingsPlugin(fp)
    
    zip = await plugin.run()

    id = event.get('id', 'event')
    title = event.get('title', 'title')
    name = 'final_proceedings'

    value = dict(
        b64=base64.b64encode(zip.getvalue()).decode('utf-8'),
        filename=f'{id}_{title}_{name}.7z'
    )

    yield dict(
        type='final',
        value=value
    )
