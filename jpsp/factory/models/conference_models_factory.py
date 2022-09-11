from typing import Any

from jpsp.models.conference import Conference, Creator, Folder, Attachment, Chair, Material, Resource, SessionSlot, \
    SessionSlotContribution, SessionSlotConvener, SessionEventConvener, SessionEvent, Speaker, PrimaryAuthor
from jpsp.utils.datetime import datedict_to_utc_ts as parse_datetime


def create_conference(conference_id: str,
                      conference_data: Any) -> Conference:
    """ """

    conference = Conference(
        id=conference_id,

        url=conference_data.get('url', None),
        title=conference_data.get('title', None),
        description=conference_data.get('description', None),

        timezone=conference_data.get('timezone', None),
        start_date=parse_datetime(conference_data.get('startDate', None)),
        end_date=parse_datetime(conference_data.get('endDate', None)),
        creation_date=parse_datetime(conference_data.get('creationDate', None)),

        room=conference_data.get('room', None),
        location=conference_data.get('location', None),
        address=conference_data.get('address', None),

        keywords=conference_data.get('keywords', []),
        organizer=conference_data.get('organizer', None),
    )

    return conference


def create_conference_creator(conference_id: str,
                              creator_data: Any) -> Creator:
    """ """

    creator = Creator(
        id=creator_data.get('id', None),

        first_name=creator_data.get('first_name', None),
        last_name=creator_data.get('last_name', None),
        affiliation=creator_data.get('affiliation', None),

        conference_id=conference_id
    )

    return creator


def create_conference_folder(conference_id: str,
                             folder_data: Any) -> Folder:
    """ """

    folder = Folder(
        id=folder_data.get('id'),

        title=folder_data.get('title'),
        description=folder_data.get('description'),
        default_folder=folder_data.get('default_folder'),
        is_protected=folder_data.get('is_protected'),

        conference_id=conference_id
    )

    return folder


def create_conference_author(conference_id: str,
                             session_slot_id: str,
                             session_slot_contribution: str,
                             author_data: dict) -> PrimaryAuthor:
    """ """

    author = PrimaryAuthor(
        id=author_data.get('id', None),

        first_name=author_data.get('first_name', None),
        last_name=author_data.get('last_name', None),

        affiliation=author_data.get('affiliation', None),
        email=author_data.get('email', None),

        contribution_id=session_slot_contribution,
        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return author


def create_conference_speaker(conference_id: str,
                              session_slot_id: str,
                              session_slot_contribution: str,
                              speaker_data: dict) -> Speaker:
    """ """

    speaker = Speaker(
        id=speaker_data.get('id', None),

        first_name=speaker_data.get('first_name', None),
        last_name=speaker_data.get('last_name', None),

        affiliation=speaker_data.get('affiliation', None),
        email=speaker_data.get('email', None),

        contribution_id=session_slot_contribution,
        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return speaker


def create_conference_folder_attachment(conference_id: str,
                                        folder_id: str,
                                        attachment_data: Any) -> Attachment:
    """ """

    attachment = Attachment(
        id=attachment_data['id'],

        title=attachment_data['title'],
        description=attachment_data['description'],
        type=attachment_data['type'],

        file_name=attachment_data['filename'],
        download_url=attachment_data['download_url'],
        content_type=attachment_data['content_type'],
        checksum=attachment_data['checksum'],
        size=attachment_data['size'],

        modified_date=parse_datetime(attachment_data['modified_dt']),

        folder_id=folder_id,
        conference_id=conference_id
    )

    return attachment


def create_conference_chair(conference_id: str,
                            chair_data: Any) -> Chair:
    """ """

    chair = Chair(
        id=chair_data['id'],

        first_name=chair_data['first_name'],
        last_name=chair_data['last_name'],
        affiliation=chair_data['affiliation'],

        conference_id=conference_id
    )

    return chair


def create_conference_material(conference_id: str,
                               material_data: Any) -> Material:
    """ """

    material = Material(
        id=material_data['id'],

        title=material_data['title'],

        conference_id=conference_id
    )

    return material


def create_conference_material_resource(conference_id: str,
                                        material_id: str,
                                        resource_data: Any) -> Resource:
    """ """

    resource = Resource(
        id=resource_data['id'],

        name=resource_data['name'],
        file_name=resource_data['fileName'],
        url=resource_data['url'],

        material_id=material_id,
        conference_id=conference_id
    )

    return resource


def create_conference_session_slot(conference_id: str,
                                   session_slot_data: Any) -> SessionSlot:
    """ """

    session_slot = SessionSlot(
        id=session_slot_data['id'],

        url=session_slot_data['url'],
        code=session_slot_data['code'],

        title=session_slot_data['title'],
        description=session_slot_data['description'],
        # note=session_slot_data['note'],

        room=session_slot_data.get('room', None),
        location=session_slot_data.get('location', None),
        address=session_slot_data.get('address', None),

        start_date=parse_datetime(session_slot_data['startDate']),
        end_date=parse_datetime(session_slot_data['endDate']),

        conference_id=conference_id
    )

    return session_slot


def create_conference_session_slot_contribution(conference_id: str,
                                                session_slot_id: str,
                                                contribution_data: Any) -> SessionSlotContribution:
    """ """

    session_slot_contribution = SessionSlotContribution(
        id=contribution_data['id'],

        type=contribution_data['type'],
        url=contribution_data['url'],
        code=contribution_data['code'],

        title=contribution_data['title'],
        session=contribution_data['session'],
        description=contribution_data['description'],

        start_date=parse_datetime(contribution_data['startDate']),
        end_date=parse_datetime(contribution_data['endDate']),
        duration=contribution_data['duration'],

        room=contribution_data.get('room', None),
        location=contribution_data.get('location', None),
        address=contribution_data.get('address', None),

        # note=contribution_data['note'],
        keywords=contribution_data['keywords'],

        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return session_slot_contribution


def create_conference_session_event(conference_id: str,
                                    session_slot_id: str,
                                    session_event_data: Any) -> SessionEvent:
    """ """

    session_event = SessionEvent(
        id=session_event_data['id'],

        code=session_event_data['code'],
        type=session_event_data['type'],
        url=session_event_data['url'],
        title=session_event_data['title'],
        description=session_event_data['description'],

        color=session_event_data['color'],
        text_color=session_event_data['textColor'],
        num_slots=session_event_data['numSlots'],

        room=session_event_data['room'],
        location=session_event_data['location'],
        address=session_event_data['address'],

        start_date=parse_datetime(session_event_data['startDate']),
        end_date=parse_datetime(session_event_data['endDate']),

        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return session_event


def create_conference_session_event_convener(conference_id: str,
                                             session_slot_id: str,
                                             session_event_id: str,
                                             convener_data: dict) -> SessionEventConvener:
    """ """

    session_event_convener = SessionEventConvener(
        id=convener_data['id'],

        title=convener_data['title'],
        first_name=convener_data['first_name'],
        last_name=convener_data['last_name'],
        affiliation=convener_data['affiliation'],

        address=convener_data.get('address', []),
        phone=convener_data.get('phone', []),
        email=convener_data.get('email', []),

        session_event_id=session_event_id,
        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return session_event_convener


def create_conference_session_slot_convener(conference_id: str,
                                            session_slot_id: str,
                                            convener_data: dict) -> SessionSlotConvener:
    """ """

    session_slot_convener = SessionSlotConvener(
        id=convener_data['id'],

        title=convener_data['title'],
        first_name=convener_data['first_name'],
        last_name=convener_data['last_name'],
        affiliation=convener_data['affiliation'],

        address=convener_data.get('address', []),
        phone=convener_data.get('phone', []),
        email=convener_data.get('email', []),

        session_slot_id=session_slot_id,
        conference_id=conference_id
    )

    return session_slot_convener
