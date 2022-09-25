import io
import logging as lg

# from PyRTF.Elements import Document
# from PyRTF.Renderer import Renderer
# from PyRTF.document.section import Section
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import H, P

from jpsp.services.local.conference.find_conference import get_conference_session_slots_entities, \
    get_conference_session_slots_conveners_entities, get_conference_session_event_entity, \
    get_conference_session_slot_contribution_entities, get_conference_session_slot_contribution_speakers_entities, \
    get_conference_session_slot_contribution_primary_authors_entities

logger = lg.getLogger(__name__)


async def create_abstract_booklet_from_event(event: dict):
    """ """

    abstract_booklet = dict(
        sessions=list()
    )

    session_slots: list[dict] = event.get('sessions', [])

    for session_slot in session_slots:

        session_event: dict = session_slot.get('session', dict())

        session_slot_data = dict(
            code=session_event.get('code'),
            title=session_slot.get('title'),
            description=session_slot.get('description'),
            room=session_slot.get('room'),
            location=session_slot.get('location'),
            address=session_slot.get('address'),
            start=session_slot.get('start_date'),
            end=session_slot.get('end_date'),
            conveners=list(),
            contributions=list()
        )

        session_slot_conveners: list[dict] = session_slot.get('conveners', [])

        for session_slot_convener in session_slot_conveners:
            session_slot_convener_data = dict(
                first=session_slot_convener.get('first_name'),
                last=session_slot_convener.get('last_name'),
                affiliation=session_slot_convener.get('affiliation')
            )

            session_slot_data['conveners'].append(session_slot_convener_data)

        session_slot_contributions: list[dict] = session_slot.get(
            'contributions', [])

        for session_slot_contribution in session_slot_contributions:
            contribution_data = dict(
                code=session_slot_contribution.get('code'),
                type=session_slot_contribution.get('type'),
                url=session_slot_contribution.get('url'),
                title=session_slot_contribution.get('title'),
                duration=session_slot_contribution.get('duration'),
                description=session_slot_contribution.get('description'),
                session=session_slot_contribution.get('session'),
                room=session_slot_contribution.get('room'),
                location=session_slot_contribution.get('location'),
                start=session_slot_contribution.get('start_date'),
                end=session_slot_contribution.get('end_date'),
                speakers=list(),
                primary_authors=list()
            )

            speakers: list[dict] = session_slot_contribution.get(
                'speakers', [])

            for speaker in speakers:
                speaker_data = dict(
                    first=speaker.get('first_name'),
                    last=speaker.get('last_name'),
                    affiliation=speaker.get('affiliation'),
                    email=speaker.get('email'),
                )

                contribution_data['speakers'].append(speaker_data)

            primary_authors: list[dict] = session_slot_contribution.get(
                'primary_authors', [])

            for primary_author in primary_authors:
                primary_author_data = dict(
                    first=primary_author.get('first_name'),
                    last=primary_author.get('last_name'),
                    affiliation=primary_author.get('affiliation'),
                    email=primary_author.get('email'),
                )

                contribution_data['primary_authors'].append(
                    primary_author_data)

            session_slot_data['contributions'].append(contribution_data)

        abstract_booklet['sessions'].append(session_slot_data)

    return abstract_booklet


async def create_abstract_booklet_from_entities(conference_id: str):
    """ """

    abstract_booklet = dict(
        sessions=list()
    )

    session_slots = await get_conference_session_slots_entities(conference_id)

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
                primary_authors=list()
            )

            speakers = await get_conference_session_slot_contribution_speakers_entities(
                conference_id, session_slot.id, session_slot_contribution.id
            )

            for speaker in speakers:
                speaker_data = dict(
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


# def export_abstract_booklet_to_rtf(abstract_booklet: dict) -> io.StringIO():
#     """ """
#
#     doc = Document()
#
#     for session in abstract_booklet['sessions']:
#         section = Section()
#
#         section.append(f"{session.get('code')} - {session.get('title')}")
#
#         doc.Sections.append(section)
#
#     f = io.StringIO()
#     Renderer().Write(doc, f)
#     f.seek(0)
#
#     return f


def export_abstract_booklet_to_odt(abstract_booklet: dict) -> io.BytesIO():
    """ """

    # 'application/vnd.oasis.opendocument.text'
    abstract_booklet_document = OpenDocumentText()

    """ """
    """ Documents styles """
    """ """
    heading_1_style = Style(name="Heading 1", family="paragraph")
    heading_1_style.addElement(TextProperties(
        attributes={'fontsize': "16pt", 'fontweight': "bold"}))

    abstract_booklet_document.styles.addElement(heading_1_style)

    heading_2_style = Style(name="Heading 2", family="paragraph")
    heading_2_style.addElement(TextProperties(
        attributes={'fontsize': "14   pt", 'fontweight': "bold"}))

    abstract_booklet_document.styles.addElement(heading_2_style)

    heading_3_style = Style(name="Heading 3", family="paragraph")
    heading_3_style.addElement(TextProperties(
        attributes={'fontsize': "12   pt", 'fontweight': "bold"}))

    abstract_booklet_document.styles.addElement(heading_3_style)
    """ """
    """ Documents styles """
    """ """

    """ """
    """ Sessions """
    """ """
    for session in abstract_booklet['sessions']:

        session_title = H(outlinelevel=1, stylename=heading_1_style,
                          text=f"{session.get('code')} - {session.get('title')}")

        abstract_booklet_document.text.addElement(session_title)

        if len(session.get('conveners')) > 0:

            session_chair = P(stylename=heading_2_style, text=f"Chair: ")

            for convener in session.get('conveners'):
                session_chair.addText(
                    f"{convener.get('first')} {convener.get('last')} ({convener.get('affiliation')})")

            abstract_booklet_document.text.addElement(session_chair)

        # Black line
        abstract_booklet_document.text.addElement(P())

        for contribution in session.get('contributions'):
            h = H(outlinelevel=1, stylename=heading_3_style,
                  text=f"{contribution.get('code')} - {contribution.get('title')}")

            abstract_booklet_document.text.addElement(h)

            c = P(text=f"{contribution.get('description')}")

            abstract_booklet_document.text.addElement(c)

            # Black line
            abstract_booklet_document.text.addElement(P())
    """ """
    """ Sessions """
    """ """

    """ """
    """ Serialization """
    """ """
    f = io.BytesIO()
    abstract_booklet_document.write(f)
    f.seek(0)
    """ """
    """ Serialization """
    """ """

    return f
