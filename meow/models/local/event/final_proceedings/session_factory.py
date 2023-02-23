import logging as lg

from typing import Any

from meow.utils.datetime import datedict_to_tz_datetime

from meow.models.local.event.final_proceedings.event_factory import event_person_factory
from meow.models.local.event.final_proceedings.session_model import SessionData


logger = lg.getLogger(__name__)


def session_data_factory(session_slot: Any) -> SessionData:

    session_event = session_slot.get('session')
    session_event_code = session_event.get('code', '')
    session_slot_code = session_slot.get('code', '')

    session_code: str = session_event_code or session_slot_code

    session_data = SessionData(
        code=session_code,
        title=session_slot.get('title'),
        url=session_slot.get('url'),
        start=datedict_to_tz_datetime(
            session_slot.get('start_dt')
        ),
        end=datedict_to_tz_datetime(
            session_slot.get('end_dt')
        ),
        is_poster=bool(session_event.get('is_poster')),
        conveners=[
            event_person_factory(person)
            for person in session_slot.get('conveners', [])
        ]
    )
    
    logger.info(session_data.as_dict())

    return session_data
