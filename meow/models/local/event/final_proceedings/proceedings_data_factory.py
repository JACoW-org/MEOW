

from typing import Any

from meow.models.local.event.final_proceedings.contribution_factory import contribution_data_factory
from meow.models.local.event.final_proceedings.event_factory import event_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_factory import session_data_factory
from meow.models.local.event.final_proceedings.session_model import SessionData

from meow.utils.sort import sort_list_by_date


def proceedings_data_factory(event: Any) -> ProceedingsData:

    sessions: list[SessionData] = [
        session_data_factory(session)
        for session in event.get('sessions', [])
    ]

    sessions.sort(key=sort_list_by_date)

    contributions = [
        contribution_data_factory(contribution)
        for contribution in event.get('contributions', [])
    ]

    contributions.sort(key=sort_list_by_date)

    return ProceedingsData(
        event=event_data_factory(event),
        sessions=sessions,
        contributions=contributions
    )
