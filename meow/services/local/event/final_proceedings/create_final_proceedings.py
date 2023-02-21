import logging as lg

from typing import Any
from meow.utils.datetime import datedict_to_tz_datetime, format_datetime_sec


logger = lg.getLogger(__name__)


def _sort_list_by_date(val):

    string = format_datetime_sec(val.get('start')) \
        + '_' + val.get('code', '')

    return string


async def create_final_proceedings(event: dict, cookies: dict, settings: dict):
    sessions = list()
    contributions = list()

    final_proceedings = dict(
        event=dict(
            id=event.get('id', ''),
            url=event.get('url', ''),
            title=event.get('title', ''),
            description=event.get('description', ''),
            location=event.get('location', ''),
            address=event.get('address', ''),
        ),
        sessions=sessions,
        contributions=contributions
    )

    for session_slot in event.get('sessions', []):

        session_event: dict = session_slot.get('session', dict())

        session_event_code = session_event.get('code', '')
        session_slot_code = session_slot.get('code', '')

        session_code: str = session_event_code or session_slot_code

        # print(session_code, session_event_code, session_slot_code)

        conveners = list()
        contributions = list()

        session_slot_data: dict[str, Any] = dict(
            code=session_code,
            title=session_slot.get('title'),
            start=datedict_to_tz_datetime(
                session_slot.get('start_dt')
            ),
            end=datedict_to_tz_datetime(
                session_slot.get('end_dt')
            ),
            is_poster=bool(session_event.get('is_poster')),
            conveners=conveners,
            contributions=contributions
        )

        session_slot_conveners: list[dict] = session_slot.get('conveners', [])

        for session_slot_convener in session_slot_conveners:
            session_slot_convener_data = dict(
                first=session_slot_convener.get('first_name'),
                last=session_slot_convener.get('last_name'),
                affiliation=session_slot_convener.get('affiliation')
            )

            conveners.append(session_slot_convener_data)

        sessions.append(session_slot_data)

    for contribution in event.get('contributions', []):

        contribution_data_speakers = list()
        contribution_data_primary_authors = list()
        contribution_data_coauthors = list()

        contribution_data = dict(
            code=contribution.get('code'),
            type=contribution.get('type'),
            url=contribution.get('url'),
            title=contribution.get('title'),
            duration=contribution.get('duration'),
            description=contribution.get('description'),
            field_values=contribution.get('field_values'),
            session=contribution.get('session'),
            room=contribution.get('room'),
            location=contribution.get('location'),
            start=datedict_to_tz_datetime(
                contribution.get('start_dt')
            ),
            end=datedict_to_tz_datetime(
                contribution.get('end_dt')
            ),
            speakers=contribution_data_speakers,
            primary_authors=contribution_data_primary_authors,
            coauthors=contribution_data_coauthors
        )

        speakers: list[dict] = contribution.get('speakers', [])

        if speakers:
            for speaker in speakers:
                speaker_data = dict(
                    id=speaker.get('id'),
                    first=speaker.get('first_name'),
                    last=speaker.get('last_name'),
                    affiliation=speaker.get('affiliation'),
                    email=speaker.get('email'),
                )

                contribution_data_speakers.append(speaker_data)

        primary_authors: list[dict] = contribution.get('primary_authors', [])

        if primary_authors:
            for primary_author in primary_authors:
                primary_author_data = dict(
                    id=primary_author.get('id'),
                    first=primary_author.get('first_name'),
                    last=primary_author.get('last_name'),
                    affiliation=primary_author.get('affiliation'),
                    email=primary_author.get('email'),
                )

                contribution_data_primary_authors.append(
                    primary_author_data)

        coauthors: list[dict] = contribution.get('coauthors', [])

        if coauthors:
            for coauthor in coauthors:
                coauthor_data = dict(
                    id=coauthor.get('id'),
                    first=coauthor.get('first_name'),
                    last=coauthor.get('last_name'),
                    affiliation=coauthor.get('affiliation'),
                    email=coauthor.get('email'),
                )

                contribution_data_coauthors.append(coauthor_data)

        contributions.append(contribution_data)

    sessions.sort(key=_sort_list_by_date)
    contributions.sort(key=_sort_list_by_date)

    return final_proceedings
