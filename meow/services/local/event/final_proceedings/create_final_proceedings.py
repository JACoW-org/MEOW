import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_factory import proceedings_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def create_final_proceedings(event: dict, cookies: dict, settings: dict) -> ProceedingsData:

    proceedings_data = proceedings_data_factory(event)
    
    # logger.info(proceedings_data.as_dict())

    return proceedings_data


