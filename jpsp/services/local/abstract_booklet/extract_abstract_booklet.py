import logging as lg

from jpsp.services.local.conference.find_conference import get_conference_session_slots_entities, \
    get_conference_session_slots_conveners_entities, get_conference_session_event_entity, \
    get_conference_session_slot_contribution_entities, get_conference_session_slot_contribution_speakers_entities, \
    get_conference_session_slot_contribution_primary_authors_entities


logger = lg.getLogger(__name__)


async def create_abstract_booklet_from_entities(conference_id: str):
    """ """

    abstract_booklet = dict(
        sessions=list()
    )

    session_slots: list | None = await get_conference_session_slots_entities(conference_id)

    if session_slots:
        for session_slot in session_slots:

            session_event = await get_conference_session_event_entity(conference_id, session_slot.id)

            session_slot_data = dict(
                code=session_event.code,
                title=session_slot.title,
                description=session_slot.description,
                room=session_slot.room,
                location=session_slot.location,
                address=session_slot.address,
                start=session_slot.start_date,
                end=session_slot.end_date,
                conveners=list(),
                contributions=list()
            )

            session_slot_conveners = await get_conference_session_slots_conveners_entities(
                conference_id, session_slot.id
            )

            for session_slot_convener in session_slot_conveners:
                session_slot_convener_data = dict(
                    first=session_slot_convener.first_name,
                    last=session_slot_convener.last_name,
                    affiliation=session_slot_convener.affiliation
                )

                session_slot_data['conveners'].append(session_slot_convener_data)

            session_slot_contributions = await get_conference_session_slot_contribution_entities(
                conference_id, session_slot.id
            )

            for session_slot_contribution in session_slot_contributions:
                contribution_data = dict(
                    code=session_slot_contribution.code,
                    type=session_slot_contribution.type,
                    url=session_slot_contribution.url,
                    title=session_slot_contribution.title,
                    duration=session_slot_contribution.duration,
                    description=session_slot_contribution.description,
                    session=session_slot_contribution.session,
                    room=session_slot_contribution.room,
                    location=session_slot_contribution.location,
                    start=session_slot_contribution.start_date,
                    end=session_slot_contribution.end_date,
                    speakers=list(),
                    primary_authors=list(),
                    coauthors=list()
                )

                speakers = await get_conference_session_slot_contribution_speakers_entities(
                    conference_id, session_slot.id, session_slot_contribution.id
                )

                for speaker in speakers:
                    speaker_data = dict(
                        id=speaker.id,
                        first=speaker.first_name,
                        last=speaker.last_name,
                        affiliation=speaker.affiliation,
                        email=speaker.email,
                    )

                    contribution_data['speakers'].append(speaker_data)

                primary_authors = await get_conference_session_slot_contribution_primary_authors_entities(
                    conference_id, session_slot.id, session_slot_contribution.id
                )

                for primary_author in primary_authors:
                    primary_author_data = dict(
                        id=primary_author.id,
                        first=primary_author.first_name,
                        last=primary_author.last_name,
                        affiliation=primary_author.affiliation,
                        email=primary_author.email,
                    )

                    contribution_data['primary_authors'].append(
                        primary_author_data)

                primary_authors = await get_conference_session_slot_contribution_primary_authors_entities(
                    conference_id, session_slot.id, session_slot_contribution.id
                )

                for primary_author in primary_authors:
                    primary_author_data = dict(
                        id=primary_author.id,
                        first=primary_author.first_name,
                        last=primary_author.last_name,
                        affiliation=primary_author.affiliation,
                        email=primary_author.email,
                    )

                    contribution_data['primary_authors'].append(
                        primary_author_data)

                session_slot_data['contributions'].append(contribution_data)

            abstract_booklet['sessions'].append(session_slot_data)

    return abstract_booklet


