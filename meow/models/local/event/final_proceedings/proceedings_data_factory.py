import logging as lg

from typing import Any, Callable

from datetime import datetime

from meow.models.local.event.final_proceedings.contribution_factory import contribution_data_factory
from meow.models.local.event.final_proceedings.event_factory import (attachment_data_factory,
                                                                     event_data_factory, event_person_factory)
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_factory import session_data_factory
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, DuplicateContributionData

from meow.utils.datetime import format_datetime_sec

from meow.utils.list import find
from meow.utils.serialization import json_decode
from meow.models.local.event.final_proceedings.event_model import PersonData


logger = lg.getLogger(__name__)


def proceedings_data_factory(event: Any, sessions: list, contributions: list,
                             attachments: list, settings: dict) -> ProceedingsData:

    logger.info('proceedings_data_factory')

    """ build editors """
    editors_dict_list = json_decode(settings.get(
        'editorial_json', '{}'))

    editors: list[PersonData] = [
        event_person_factory(person)
        for person in editors_dict_list
    ]

    """ create sessions data """

    sessions_data: list[SessionData] = [
        session_data_factory(session)
        for session in sessions
    ]

    """ create contributions data """

    contributions_data: list[ContributionData] = [
        c for c in [
            contribution_data_factory(c, editors) for c in contributions
        ] if c and c.cat_publish
    ]

    """ sort sessions data """

    sessions_data.sort(key=lambda x: (
        format_datetime_sec(x.start),
        x.code
    ))

    """ filter sessions with no contributions"""

    sessions_counts: dict[str, int] = {
        f'{s.code}': sum(map(lambda c: c.session_code == s.code, contributions_data))
        for s in sessions_data
    }

    # logger.info(sessions_counts)

    sessions_data = [
        s for s in sessions_data
        if sessions_counts[s.code] > 0
    ]

    """ resolve contributions duplicates_of """

    # resolve duplicate of
    # contributions_data = resolve_duplicates_of(contributions_data)

    """ sort contributions data """

    sessions_dates: dict[str, datetime] = {
        f'{session.code}': session.start
        for session in sessions_data
    }

    contributions_data.sort(key=lambda x: (
        format_datetime_sec(
            sessions_dates.get(x.session_code)),                    # session date
        x.session_code,                                             # session code
        x.code                                                      # contribution code
    ))

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
        duplicate_of_code: str | None = contribution.duplicate_of_code
        if duplicate_of_code:
            predicate = find_predicate(duplicate_of_code)
            duplicate_contribution: ContributionData | None = find(
                contributions, predicate)
            if duplicate_contribution and duplicate_contribution.metadata:
                logger.info(
                    f"Contribution {contribution.code} has duplicate {contribution.duplicate_of_code} with metadata")
            contribution.duplicate_of = DuplicateContributionData(
                code=duplicate_contribution.code,
                session_code=duplicate_contribution.session_code,
                has_metadata=True if duplicate_contribution.metadata else False,
                doi_url=duplicate_contribution.doi_data.doi_url if duplicate_contribution.doi_data else '',
                reception=duplicate_contribution.reception,
                revisitation=duplicate_contribution.revisitation,
                acceptance=duplicate_contribution.acceptance,
                issuance=duplicate_contribution.issuance
            ) if duplicate_contribution else None
    return contributions


def find_predicate(code: str) -> Callable[..., bool]:

    def _predicate(c: ContributionData) -> bool:
        return c.code == code

    return _predicate
