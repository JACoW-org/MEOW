import logging as lg

from meow.models.local.event.final_proceedings.proceedings_data_factory import proceedings_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def adapting_proceedings(event: dict, sessions: list, contributions: list, attachments: list,
                                     cookies: dict, settings: dict) -> ProceedingsData:
    """ """

    logger.info('event_final_proceedings - adapting_final_proceedings')

    proceedings_data = proceedings_data_factory(
        event, sessions, contributions, attachments, settings)

    # logger.info(proceedings_data.as_dict())

    # raise BaseException()

    return proceedings_data
