

from typing import Any

from meow.models.local.event.final_proceedings.contribution_factory import contribution_data_factory
from meow.models.local.event.final_proceedings.event_factory import attachment_data_factory, event_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_factory import session_data_factory
from meow.models.local.event.final_proceedings.session_model import SessionData

from meow.utils.sort import sort_list_by_code, sort_list_by_date


def proceedings_data_factory(event: Any, sessions: list, contributions: list, attachments: list, settings: dict) -> ProceedingsData:

    sessions_data: list[SessionData] = [
        session_data_factory(session)
        for session in sessions
    ]

    sessions_data.sort(key=sort_list_by_date)

    contributions_data = [
        contribution_data_factory(contribution)
        for contribution in contributions
    ]

    contributions_data.sort(key=sort_list_by_code)
    
    attachments_data = [
        attachment_data_factory(attachment)
        for attachment in attachments
    ]

    return ProceedingsData(
        event=event_data_factory(event, settings),
        sessions=sessions_data,
        contributions=contributions_data,
        attachments=attachments_data
    )
