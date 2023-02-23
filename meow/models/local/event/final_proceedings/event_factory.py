import logging as lg

from typing import Any

from meow.models.local.event.final_proceedings.event_model import EventData, EventPersonData
from meow.utils.datetime import datedict_to_tz_datetime


logger = lg.getLogger(__name__)


def event_data_factory(event: Any) -> EventData:
    return EventData(
        id=event.get('id'),
        url=event.get('url'),
        title=event.get('title'),
        description=event.get('description'),
        location=event.get('location'),
        address=event.get('address'),
        start=datedict_to_tz_datetime(
            event.get('start_dt')
        ),
        end=datedict_to_tz_datetime(
            event.get('end_dt')
        ),
    )


def event_person_factory(person: Any) -> EventPersonData:
    return EventPersonData(
        id=person.get('id'),
        first=person.get('first_name'),
        last=person.get('last_name'),
        affiliation=person.get('affiliation'),
        email=person.get('email'),
    )
