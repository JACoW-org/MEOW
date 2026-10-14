import logging as lg

from typing import Any

from datetime import datetime

from meow.models.local.event.final_proceedings.contribution_factory import contribution_data_factory
from meow.models.local.event.final_proceedings.event_factory import (material_data_factory,
                                                                     event_data_factory, event_person_factory)
from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData
from meow.models.local.event.final_proceedings.session_factory import session_data_factory
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, DuplicateContributionData

from meow.utils.datetime import format_datetime_sec

from meow.services.local.event.final_proceedings.manage_duplicates import (
    find_duplicate_contribution,
)
from meow.utils.serialization import json_decode
from meow.models.local.event.final_proceedings.event_model import PersonData


logger = lg.getLogger(__name__)


def proceedings_data_factory(event: Any, sessions: list, contributions: list,
                             materials: list, settings: dict) -> ProceedingsData:

    logger.info('proceedings_data_factory')

    event_timezone: str = event.get('timezone', '')

    """ build editors """
    
    editors_dict_list = json_decode(settings.get(
        'editorial_json', '{}'))

    editors: list[PersonData] = [
        event_person_factory(person)
        for person in editors_dict_list
    ]

    """ create sessions data """

    sessions_data: list[SessionData] = [
        session_data_factory(session, event_timezone)
        for session in sessions
    ]

    """ create contributions data """

    cat_publish_alias: str | None = settings.get('cat_publish_alias', 'CAT_publish')

    preprint_marking_alias: str | None = settings.get('preprint_marking_alias', 'CAT_preprint_marking')
    preprint_request_alias: str | None = settings.get('preprint_request_alias')

    contributions_data: list[ContributionData] = [
        c for c in [
            contribution_data_factory(c, editors, event_timezone, preprint_marking_alias, preprint_request_alias) for c in contributions
        ] if c and c.cat_publish(cat_publish_alias)
    ]

    """ sort sessions data """

    sessions_data.sort(key=lambda x: (
        format_datetime_sec(x.start),
        x.code,
        x.id
    ))

    """ filter sessions with no contributions"""

    sessions_counts: dict[int, int] = {
        s.id: sum(map(lambda c: c.session_id == s.id, contributions_data))
        for s in sessions_data
    }

    # logger.info(sessions_counts)

    sessions_data = [
        s for s in sessions_data
        if sessions_counts[s.id] > 0
    ]

    """ resolve contributions duplicates_of """

    # resolve duplicate of
    # contributions_data = resolve_duplicates_of(contributions_data)

    """ sort contributions data """

    sessions_dates: dict[int, datetime] = {
        session.id: session.start
        for session in sessions_data
    }

    contributions_data.sort(key=lambda c: (
        format_datetime_sec(
            sessions_dates.get(c.session_id)),                    # session date
        c.session_code,                                           # session id
        c.session_id,                                             # session code
        c.code                                                    # contribution code
    ))

    materials_data = [
        material_data_factory(material)
        for material in materials
    ]

    return ProceedingsData(
        event=event_data_factory(event, settings),
        sessions=sessions_data,
        contributions=contributions_data,
        materials=materials_data
    )


def resolve_duplicates_of(contributions: list[ContributionData], settings: dict) -> list[ContributionData]:
    duplicate_of_alias = settings.get('duplicate_of_alias', 'duplicate_of')
    for contribution in contributions:
        duplicate_of_code: str | None = contribution.duplicate_of_code(duplicate_of_alias)
        if duplicate_of_code:
            duplicate_contribution: ContributionData | None = find_duplicate_contribution(
                contributions, duplicate_of_code, current_contribution=contribution
            )
            if duplicate_contribution and duplicate_contribution.metadata:
                logger.info(
                    f"Contribution {contribution.code} has duplicate {duplicate_of_code} with metadata")
            if duplicate_contribution:
                contribution.duplicate_of = DuplicateContributionData(
                    code=duplicate_contribution.code,
                    session_id=duplicate_contribution.session_id,
                    session_code=duplicate_contribution.session_code,
                    has_metadata=True if duplicate_contribution.metadata else False,
                    doi_url=duplicate_contribution.doi_data.doi_url if duplicate_contribution.doi_data else '',
                    reception=duplicate_contribution.reception,
                    revisitation=duplicate_contribution.revisitation,
                    acceptance=duplicate_contribution.acceptance,
                    issuance=duplicate_contribution.issuance
                )
                if duplicate_contribution.title is not None:
                    contribution.title = duplicate_contribution.title
                if duplicate_contribution.description is not None:
                    contribution.description = duplicate_contribution.description
                contribution.primary_authors = list(duplicate_contribution.primary_authors)
                contribution.coauthors = list(duplicate_contribution.coauthors)
                contribution.authors = list(duplicate_contribution.authors)
                contribution.institutes = list(duplicate_contribution.institutes)
                if duplicate_contribution.keywords:
                    contribution.keywords = list(duplicate_contribution.keywords)
            else:
                contribution.duplicate_of = None
    return contributions
