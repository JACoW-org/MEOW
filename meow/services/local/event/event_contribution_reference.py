import logging as lg

from typing import AsyncGenerator
from meow.services.local.event.final_proceedings.create_final_proceedings import create_final_proceedings

from meow.services.local.event.final_proceedings.extract_contribution_references import extract_contribution_references

logger = lg.getLogger(__name__)

async def event_contribution_reference(event: dict, cookies: dict, settings: dict) -> AsyncGenerator:
    """ """

    final_proceedings = await create_final_proceedings(event, cookies, settings)
    
    final_proceedings = await extract_contribution_references(final_proceedings, cookies, settings)
    
    yield dict(
        type='final',
        value=final_proceedings
    )
