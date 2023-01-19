import base64
import logging as lg

from typing import AsyncGenerator

from jpsp.services.local.event.abstract_booklet.create_abstract_booklet \
    import create_abstract_booklet_from_event

from jpsp.services.local.event.abstract_booklet.export_abstract_booklet \
    import export_abstract_booklet_to_odt


logger = lg.getLogger(__name__)


async def event_abstract_booklet(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    ab = await create_abstract_booklet_from_event(event, cookies, settings)

    odt = export_abstract_booklet_to_odt(ab, event, cookies, settings)

    id = event.get('id', 'event')
    title = event.get('title', 'title')
    name = 'abstrack_booklet'

    result = dict(
        b64=base64.b64encode(odt.getvalue()).decode('utf-8'),
        filename=f'{id}_{title}_{name}.odt'
    )

    yield dict(
        type='final',
        value=result
    )
