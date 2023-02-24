import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def refill_papers_metadata(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """
    
    return proceedings_data