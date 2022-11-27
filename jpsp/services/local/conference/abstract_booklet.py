import io
import logging as lg
import functools

from itertools import groupby
from operator import itemgetter

# from PyRTF.Elements import Document
# from PyRTF.Renderer import Renderer
# from PyRTF.document.section import Section
from odf.opendocument import OpenDocumentText, OpenDocument
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import Span, P

from jpsp.utils.datetime import datedict_to_tz_datetime, format_datetime_day, format_datetime_range, format_datetime_time

from jpsp.services.local.conference.find_conference import get_conference_session_slots_entities, \
    get_conference_session_slots_conveners_entities, get_conference_session_event_entity, \
    get_conference_session_slot_contribution_entities, get_conference_session_slot_contribution_speakers_entities, \
    get_conference_session_slot_contribution_primary_authors_entities

logger = lg.getLogger(__name__)


async def create_abstract_booklet_from_event(event: dict) -> dict:
    """ """

    def sort_list_by_date(val):
        return format_datetime_day(val.get('start')) \
            + '_' + val.get('code')

    sessions = list()

    abstract_booklet = dict(
        event=dict(
            url=event.get('url', ''),
            title=event.get('title', ''),
            description=event.get('description', ''),
            location=event.get('location', ''),
            address=event.get('address', ''),
        ),
        sessions=sessions
    )

    session_slots: list[dict] = event.get('sessions', [])

    for session_slot in session_slots:

        session_event: dict = session_slot.get('session', dict())

        conveners = list()
        contributions = list()

        session_slot_data = dict(
            code=session_event.get('code'),
            title=session_slot.get('title'),
            description=session_slot.get('description'),
            room=session_slot.get('room'),
            location=session_slot.get('location'),
            address=session_slot.get('address'),
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
                start=datedict_to_tz_datetime(
                    session_slot_contribution.get('start_dt')
                ),
                end=datedict_to_tz_datetime(
                    session_slot_contribution.get('end_dt')
                ),
                speakers=list(),
                primary_authors=list(),
                coauthors=list()
            )

            speakers: list[dict] = session_slot_contribution.get(
                'speakers', [])

            for speaker in speakers:
                speaker_data = dict(
                    id=speaker.get('id'),
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
                    id=primary_author.get('id'),
                    first=primary_author.get('first_name'),
                    last=primary_author.get('last_name'),
                    affiliation=primary_author.get('affiliation'),
                    email=primary_author.get('email'),
                )

                contribution_data['primary_authors'].append(
                    primary_author_data)

            coauthors: list[dict] = session_slot_contribution.get(
                'coauthors', [])

            for coauthor in coauthors:
                coauthor_data = dict(
                    id=coauthor.get('id'),
                    first=coauthor.get('first_name'),
                    last=coauthor.get('last_name'),
                    affiliation=coauthor.get('affiliation'),
                    email=coauthor.get('email'),
                )

                contribution_data['coauthors'].append(
                    coauthor_data)

            contributions.append(contribution_data)

        sessions.append(session_slot_data)

        contributions.sort(key=sort_list_by_date)

    sessions.sort(key=sort_list_by_date)

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


def export_abstract_booklet_to_odt(abstract_booklet_data: dict) -> io.BytesIO:
    """ """

    def _serialize_abstract_booklet(abstract_booklet_document: OpenDocument):
        """ Serialization """

        f = io.BytesIO()
        abstract_booklet_document.write(f)
        f.seek(0)

        return f

    def _document_styles(abstract_booklet_document: OpenDocument):
        """ Documents styles """

        root_style = Style(name="AB Root", family="paragraph")

        root_style.addElement(TextProperties(attributes={
            'fontfamily': "'Arial'"
        }))

        abstract_booklet_document.styles.addElement(root_style)

        heading_1_style = Style(name="AB Heading 1", family="paragraph")

        heading_1_style.addElement(TextProperties(attributes={
            'fontsize': "16pt",
            'fontweight': "bold",
            'color': '#ff0000'
        }))

        heading_1_style.addElement(ParagraphProperties(
            breakbefore="page",
            keepwithnext="always"
        ))

        abstract_booklet_document.styles.addElement(heading_1_style)

        heading_2_style = Style(name="AB Heading 2", family="paragraph")

        heading_2_style.addElement(TextProperties(attributes={
            'fontsize': "14pt",
            'fontweight': "bold",
            'color': '#ff0000'
        }))

        heading_2_style.addElement(ParagraphProperties(
            keepwithnext="always"
        ))

        abstract_booklet_document.styles.addElement(heading_2_style)

        heading_3_style = Style(name="AB Heading 3", family="paragraph")

        heading_3_style.addElement(TextProperties(attributes={
            # 'fontsize': "12pt",
            'fontweight': "bold",
            'color': '#ff0000'
        }))

        heading_3_style.addElement(ParagraphProperties(
            keepwithnext="always"
        ))

        abstract_booklet_document.styles.addElement(heading_3_style)

        heading_4_style = Style(name="AB Title", family="paragraph")

        heading_4_style.addElement(TextProperties(attributes={
            # 'fontsize': "12pt",
            'fontweight': "bold"
        }))

        abstract_booklet_document.styles.addElement(heading_4_style)

        heading_5_style = Style(name="AB Authors", family="paragraph")

        heading_5_style.addElement(TextProperties(attributes={
            # 'fontsize': "12pt",
            'fontstyle': "italic"
        }))

        abstract_booklet_document.styles.addElement(heading_5_style)

        heading_6_style = Style(name="AB Speakers", family="text")

        heading_6_style.addElement(TextProperties(fontweight="bold"))

        abstract_booklet_document.styles.addElement(heading_6_style)

        heading_7_style = Style(name="AB Coauthors", family="paragraph")

        heading_7_style.addElement(TextProperties(attributes={
            # 'fontsize': "12pt",
            'fontstyle': "italic"
        }))

        abstract_booklet_document.styles.addElement(heading_7_style)

        description_style = Style(name="AB Description", family="paragraph")

        description_style.addElement(TextProperties(attributes={
            # 'fontsize': "12pt"
        }))

        abstract_booklet_document.styles.addElement(description_style)

        footnotes_style = Style(name="AB Footnotes", family="paragraph")

        footnotes_style.addElement(TextProperties(attributes={
            'fontsize': "12pt"
        }))

        abstract_booklet_document.styles.addElement(footnotes_style)

        funding_agency_style = Style(name="AB Funding Agency", family="paragraph")

        funding_agency_style.addElement(TextProperties(attributes={
            'fontsize': "12pt"
        }))

        abstract_booklet_document.styles.addElement(funding_agency_style)

        return dict(
            rt=root_style,
            h1=heading_1_style,
            h2=heading_2_style,
            h3=heading_3_style,
            h4=heading_4_style,
            h5=heading_5_style,
            h6=heading_6_style,
            h7=heading_7_style,
            de=description_style,
            fn=footnotes_style,
            fa=funding_agency_style,
        )

    def _abstract_booklet_chapters(abstract_booklet_document: OpenDocument, abstract_booklet: dict, heading_styles: dict):
        """ Sessions """

        for session in abstract_booklet['sessions']:

            print(session.get('code'), session.get('title'),
                  session.get('start'), session.get('end'))

            session_code = f"{session.get('code')}"
            session_title = f"{session.get('title')}"

            session_date = format_datetime_range(session.get('start'),
                                                 session.get('end'))

            abstract_booklet_document.text.addElement(  # type: ignore
                P(stylename=heading_styles.get('h1'),
                  text=f"{session_code} - {session_title}")
            )

            abstract_booklet_document.text.addElement(  # type: ignore
                P(stylename=heading_styles.get('h2'),
                  text=f"{session_date}")
            )

            if len(session.get('conveners')) > 0:

                session_chair = P(stylename=heading_styles.get('h2'),
                                  text=f"Chair: ")

                for convener in session.get('conveners'):
                    session_chair.addText(
                        f"{convener.get('first')} {convener.get('last')} ({convener.get('affiliation')})"
                    )

                abstract_booklet_document.text.addElement(  # type: ignore
                    session_chair
                )

            # Black line
            abstract_booklet_document.text.addElement(P())  # type: ignore

            for contribution in session.get('contributions'):

                contribution_start = "/ " + format_datetime_time(
                    contribution.get('start')
                ) if not session.get('is_poster') else ''

                contribution_speakers_ids = [
                    int(item.get('id')) for item in contribution.get('speakers', [])
                ]

                contribution_primary_authors_groups = [
                    ({'key': key, 'items': [item for item in items]})

                    for (key, items) in groupby(contribution.get(
                        'primary_authors', []), itemgetter('affiliation'))
                ]

                contribution_coauthors_groups = [
                    ({'key': key, 'items': [item for item in items]})

                    for (key, items) in groupby(contribution.get(
                        'coauthors', []), itemgetter('affiliation'))
                ]

                contribution_coauthors_values = [
                    (
                        f"{item.get('first', '')} {item.get('last')} ({item.get('affiliation')})"
                        if index == len(g.get('items', []))-1 else f"{item.get('first')} {item.get('last')}"
                    )
                    for g in contribution_coauthors_groups
                    for index, item in enumerate(g.get('items', []))
                ]

                abstract_booklet_document.text.addElement(  # type: ignore
                    P(stylename=heading_styles.get('h3'),
                      text=f"{contribution.get('code')} {contribution_start}")
                )

                abstract_booklet_document.text.addElement(  # type: ignore
                    P(stylename=heading_styles.get('h4'),
                      text=f"{contribution.get('title')}")
                )

                contribution_primary_authors_para = P(stylename=heading_styles.get('h5'))

                if contribution_primary_authors_groups:
                    for group_idx, group in enumerate(contribution_primary_authors_groups):
                        for item_idx, item in enumerate(group.get('items', [])):

                            # print(item.get('id'), contribution_speakers_ids, (int(item.get('id')) in contribution_speakers_ids))

                            stylename = heading_styles.get('h6') if int(item.get('id')) in contribution_speakers_ids else None

                            separator = "" if group_idx == len(
                                contribution_primary_authors_groups) - 1 else ", "

                            text = f"{item.get('first', '')} {item.get('last')} " \
                                + f"({item.get('affiliation')})" \
                                if item_idx == len(group.get('items', []))-1 \
                                else f"{item.get('first')} {item.get('last')}"

                            contribution_primary_authors_para.addElement(  # type: ignore
                                Span(stylename=stylename, text=text)
                            )

                            contribution_primary_authors_para.addElement(  # type: ignore
                                Span(text=separator)
                            )
                            
                abstract_booklet_document.text.addElement(  # type: ignore
                    contribution_primary_authors_para
                )

                contribution_coauthors_para = P(stylename=heading_styles.get('h7'))
                
                if contribution_coauthors_groups:
                    for group_idx, group in enumerate(contribution_coauthors_groups):
                        for item_idx, item in enumerate(group.get('items', [])):

                            separator = "" if group_idx == len(
                                contribution_coauthors_groups) - 1 else ", "

                            text = f"{item.get('first', '')} {item.get('last')} " \
                                + f"({item.get('affiliation')})" + separator \
                                if item_idx == len(group.get('items', []))-1 \
                                else f"{item.get('first')} {item.get('last')}"

                            contribution_coauthors_para.addElement(  # type: ignore
                                Span(text=text)
                            )

                            contribution_coauthors_para.addElement(  # type: ignore
                                Span(text=separator)
                            )
                            
                abstract_booklet_document.text.addElement(  # type: ignore
                    contribution_coauthors_para
                )

                # Black line
                abstract_booklet_document.text.addElement(P())  # type: ignore

                # parametrizzazione
                # session h1: {code} - {title}
                # session h2: {start} - {end}
                # contribution: {code} / {time}

                # Campi opzionali - con stili specifici

                # Description
                description_lines = contribution.get(
                    'description', '').splitlines()

                for description in description_lines:
                    abstract_booklet_document.text.addElement(  # type: ignore
                        P(stylename=heading_styles.get('de'),
                          text=f"{description}")
                    )

                # Footnotes
                footnotes_lines = contribution.get(
                    'footnotes', '').splitlines()

                for footnotes in footnotes_lines:
                    abstract_booklet_document.text.addElement(  # type: ignore
                        P(stylename=heading_styles.get('fn'),
                          text=f"{footnotes}")
                    )

                # Funding Agency
                funding_agency_lines = contribution.get(
                    'funding_agency', '').splitlines()

                for funding_agency in funding_agency_lines:
                    abstract_booklet_document.text.addElement(  # type: ignore
                        P(stylename=heading_styles.get('fa'),
                          text=f"{funding_agency}")
                    )

                # Black line
                abstract_booklet_document.text.addElement(P())  # type: ignore

        return abstract_booklet_document

    # 'application/vnd.oasis.opendocument.text'
    abstract_booklet_document: OpenDocument = OpenDocumentText()

    heading_styles = _document_styles(abstract_booklet_document)

    # abstract_booklet_document = _abstract_booklet_index(abstract_booklet_document,
    #                                                        abstract_booklet_data,
    #                                                        heading_styles)

    abstract_booklet_document = _abstract_booklet_chapters(abstract_booklet_document,
                                                           abstract_booklet_data,
                                                           heading_styles)

    return _serialize_abstract_booklet(abstract_booklet_document)
