import logging as lg

from typing import Any
from meow.utils.datetime import datedict_to_tz_datetime, datetime_localize, format_datetime_sec


logger = lg.getLogger(__name__)


async def create_abstract_booklet_from_event(event: dict, sessions: list, contributions: list) -> dict:
    """ """

    # for c in contributions:
    #     logger.info(f"{c.get('code')} -> {c.get('session_code')}")

    event_url = event.get('url', '')
    event_title = event.get('title', '')
    event_description = event.get('description', ''),
    event_location = event.get('location', ''),
    event_address = event.get('address', ''),
    event_timezone = event.get('timezone', '')

    sessions_data = list()

    abstract_booklet = dict(
        event=dict(
            url=event_url,
            title=event_title,
            description=event_description,
            location=event_location,
            address=event_address,
            timezone=event_timezone,
        ),
        sessions=sessions_data
    )

    for session_slot in sessions:

        session_event: dict = session_slot.get('session', dict())

        session_id = session_slot.get('id', 0)
        session_slot_code = session_slot.get('code', '')
        session_event_code = session_event.get('code', '')

        session_code: str = session_slot_code or session_event_code

        # print(session_code, session_event_code, session_slot_code)

        conveners_data = list()
        contributions_data = list()

        session_slot_data: dict[str, Any] = dict(
            id=session_id,
            code=session_code,
            title=session_slot.get('title'),
            description=session_slot.get('description'),
            room=session_slot.get('room'),
            location=session_slot.get('location'),
            address=session_slot.get('address'),
            start=datetime_localize(
                datedict_to_tz_datetime(
                    session_slot.get('start_dt')
                ), event_timezone
            ),
            end=datetime_localize(
                datedict_to_tz_datetime(
                    session_slot.get('end_dt')
                ), event_timezone
            ),
            is_poster=bool(session_event.get('is_poster')),
            conveners=conveners_data,
            contributions=contributions_data
        )

        session_slot_conveners: list[dict] = session_slot.get(
            'conveners', [])

        for session_slot_convener in session_slot_conveners:
            session_slot_convener_data = dict(
                first=session_slot_convener.get('first_name'),
                last=session_slot_convener.get('last_name'),
                affiliations=_get_affiliations(
                    session_slot_convener.get('affiliation', None),
                    session_slot_convener.get('multiple_affiliations', [])
                )
            )

            conveners_data.append(session_slot_convener_data)

        session_slot_contributions: list[dict] = [
            c for c in contributions
            if c.get('session_id') == session_id
        ]

        # session_slot_contributions_len = len(session_slot_contributions)

        # logger.info(
        #     f"session_code: {session_code} - session_slot_contributions_len: {session_slot_contributions_len}")

        if session_slot_contributions:
            for session_slot_contribution in session_slot_contributions:

                contribution_data_speakers = list()
                contribution_data_primary_authors = list()
                contribution_data_coauthors = list()

                contribution_data = dict(
                    code=session_slot_contribution.get('code'),
                    type=session_slot_contribution.get('type'),
                    url=session_slot_contribution.get('url'),
                    title=session_slot_contribution.get('title'),
                    duration=session_slot_contribution.get('duration'),
                    description=session_slot_contribution.get(
                        'description'),
                    field_values=session_slot_contribution.get(
                        'field_values'),
                    session=session_slot_contribution.get('session'),
                    room=session_slot_contribution.get('room'),
                    location=session_slot_contribution.get('location'),
                    start=datetime_localize(
                        datedict_to_tz_datetime(
                            session_slot_contribution.get('start_dt')
                        ), event_timezone
                    ),
                    # datedict_to_tz_datetime(
                    #    session_slot_contribution.get('start_dt')
                    # ),
                    end=datetime_localize(
                        datedict_to_tz_datetime(
                            session_slot_contribution.get('end_dt')
                        ), event_timezone
                    ),
                    # end=datedict_to_tz_datetime(
                    #     session_slot_contribution.get('end_dt')
                    # ),
                    speakers=contribution_data_speakers,
                    primary_authors=contribution_data_primary_authors,
                    coauthors=contribution_data_coauthors
                )

                speakers: list[dict] = session_slot_contribution.get(
                    'speakers', [])

                if speakers:
                    for speaker in speakers:
                        speaker_data = dict(
                            id=speaker.get('id'),
                            first=speaker.get('first_name'),
                            last=speaker.get('last_name'),
                            # affiliation=speaker.get('affiliation'),
                            affiliations=_get_affiliations(
                                speaker.get('affiliation', None),
                                speaker.get('multiple_affiliations', [])
                            ),
                            email=speaker.get('email'),
                        )

                        contribution_data_speakers.append(speaker_data)

                primary_authors: list[dict] = session_slot_contribution.get(
                    'primary_authors', [])

                if primary_authors:
                    for primary_author in primary_authors:
                        primary_author_data = dict(
                            id=primary_author.get('id'),
                            first=primary_author.get('first_name'),
                            last=primary_author.get('last_name'),
                            # affiliation=primary_author.get('affiliation'),
                            affiliations=_get_affiliations(
                                primary_author.get('affiliation', None),
                                primary_author.get('multiple_affiliations', [])
                            ),
                            email=primary_author.get('email'),
                        )

                        contribution_data_primary_authors.append(
                            primary_author_data)

                coauthors: list[dict] = session_slot_contribution.get(
                    'coauthors', [])

                if coauthors:
                    for coauthor in coauthors:
                        coauthor_data = dict(
                            id=coauthor.get('id'),
                            first=coauthor.get('first_name'),
                            last=coauthor.get('last_name'),
                            # affiliation=coauthor.get('affiliation'),
                            affiliations=_get_affiliations(
                                coauthor.get('affiliation', None),
                                coauthor.get('multiple_affiliations', [])
                            ),
                            email=coauthor.get('email'),
                        )

                        contribution_data_coauthors.append(coauthor_data)

                contributions_data.append(contribution_data)

        contributions_data.sort(key=lambda x: (
            x.get('code', '')
        ))

        sessions_data.append(session_slot_data)

    sessions_data.sort(key=lambda x: (
        format_datetime_sec(x.get('start', '')),
        x.get('code', ''),
        x.get('id', 0),
    ))

    return abstract_booklet


def _get_affiliations(affiliation: str, multiple_affiliations: list[str]) -> set[str]:
    affiliations = [affiliation] if affiliation else []

    return set(affiliations + multiple_affiliations)
