import logging as lg

from typing import AsyncGenerator

logger = lg.getLogger(__name__)

async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """
    
    yield dict(
        type='final',
        value=None
    )
