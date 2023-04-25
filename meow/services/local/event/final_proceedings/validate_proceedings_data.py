import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData


logger = lg.getLogger(__name__)


async def validate_proceedings_data(proceedings_data: ProceedingsData, cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - validate_events_data')
    
    return proceedings_data