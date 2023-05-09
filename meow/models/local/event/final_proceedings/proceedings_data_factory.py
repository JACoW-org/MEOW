

from typing import Any

from meow.models.local.event.final_proceedings.contribution_factory import contribution_data_factory
from meow.models.local.event.final_proceedings.event_factory import attachment_data_factory, event_data_factory
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_factory import session_data_factory
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, DuplicateContributionData

from meow.utils.sort import sort_list_by_code, sort_list_by_date

from pydash import find


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

    # resolve duplicate of
    contributions_data = resolve_duplicates_of(contributions_data)

    # TODO by session_date, session_code, by contribution_code
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

def resolve_duplicates_of(contributions: list[ContributionData]) -> list[ContributionData]:
    for contribution in contributions:
        duplicate_of_code: str = contribution.duplicate_of_code()
        if duplicate_of_code:
            duplicate_contribution: ContributionData = find(contributions, lambda contrib: contrib.code == duplicate_of_code)
            contribution.duplicate_of = DuplicateContributionData(
                code=duplicate_contribution.code,
                session_code=duplicate_contribution.session_code
            )
    return contributions
