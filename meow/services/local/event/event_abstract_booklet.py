import base64
import logging as lg

from typing import AsyncGenerator

from meow.services.local.event.abstract_booklet.collect_sessions_and_contributions import (
    collect_sessions_and_contributions)
from meow.services.local.event.abstract_booklet.create_abstract_booklet import create_abstract_booklet_from_event
from meow.services.local.event.abstract_booklet.export_abstract_booklet import export_abstract_booklet_to_odt


logger = lg.getLogger(__name__)


async def event_abstract_booklet(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    logger.info('event_abstract_booklet - collect_sessions_and_contributions')

    yield dict(type='progress', value=dict(
        phase='collect_sessions_and_contributions',
        text="Collecting sessions and contributions"
    ))

    [sessions, contributions] = await collect_sessions_and_contributions(event, cookies, settings)

    # logger.info(f'event_abstract_booklet - sessions_len: {len(sessions)}' +
    #             f' - contributions_len: { len(contributions)}')

    """ """

    logger.info('event_abstract_booklet - create_abstract_booklet_from_event')

    yield dict(type='progress', value=dict(
        phase='create_abstract_booklet_from_event',
        text="Create Abstract Booklet From Event"
    ))

    ab = await create_abstract_booklet_from_event(event, sessions, contributions)

    """ """

    logger.info('event_abstract_booklet - export_abstract_booklet_to_odt')

    yield dict(type='progress', value=dict(
        phase='export_abstract_booklet_to_odt',
        text="Export Abstract Booklet To ODT"
    ))

    odt = export_abstract_booklet_to_odt(ab, cookies, settings)

    id = event.get('id', 'event')
    title = event.get('title', 'title')
    name = 'abstrack_booklet'

    result = dict(
        b64=base64.b64encode(odt.getvalue()).decode('utf-8'),
        filename=f'{id}_{title}_{name}.odt'
    )

    yield dict(
        type='result',
        value=result
    )
