import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_factory import proceedings_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def adapting_proceedings(event: dict, sessions: list, contributions: list, materials: list,
                                     cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    logger.info('event_proceedings - adapting_proceedings')

    proceedings_data = proceedings_data_factory(
        event, sessions, contributions, materials, settings)

    # logger.info(proceedings_data.as_dict())

    # raise BaseException()

    return proceedings_data
