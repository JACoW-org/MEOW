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
from odf.text import TableOfContent, TableOfContentSource, TableOfContentEntryTemplate
from odf.text import IndexBody, IndexTitle, Tab, BookmarkStart, BookmarkEnd, BookmarkRef

from jpsp.utils.datetime import format_datetime_time, format_datetime_full

logger = lg.getLogger(__name__)


def _serialize_abstract_booklet(odt: OpenDocument):
    """ Serialization """

    f = io.BytesIO()
    odt.write(f)
    f.seek(0)

    return f


def _document_styles(odt: OpenDocument):
    """ Documents styles """

    root_style = Style(name="AB Root", family="paragraph")

    root_style.addElement(TextProperties(fontfamily='Arial'))

    odt.styles.addElement(root_style)

    h1_style = Style(name="AB Heading 1", family="paragraph")

    h1_style.addElement(TextProperties(
        fontsize="16pt", fontweight="bold", color='#ff0000'))

    h1_style.addElement(ParagraphProperties(
        breakbefore="page", keepwithnext="always"))

    odt.styles.addElement(h1_style)

    h2_style = Style(name="AB Heading 2", family="paragraph")

    h2_style.addElement(TextProperties(
        fontsize="14pt", fontweight="bold", color='#ff0000'))

    h2_style.addElement(ParagraphProperties(keepwithnext="always"))

    odt.styles.addElement(h2_style)

    h3_style = Style(name="AB Heading 3", family="paragraph")

    h3_style.addElement(TextProperties(
        fontsize="12pt", fontweight="bold", color='#ff0000'))

    h3_style.addElement(ParagraphProperties(keepwithnext="always"))

    odt.styles.addElement(h3_style)

    title_style = Style(name="AB Title", family="paragraph")

    title_style.addElement(TextProperties(
        fontsize="12pt", fontweight="bold"))

    odt.styles.addElement(title_style)

    authors_style = Style(name="AB Authors", family="paragraph")

    authors_style.addElement(TextProperties(
        fontsize="12pt", fontstyle="italic"))

    odt.styles.addElement(authors_style)

    speakers_style = Style(name="AB Speakers", family="text")

    speakers_style.addElement(TextProperties(fontweight="bold"))

    odt.styles.addElement(speakers_style)

    coauthors_style = Style(name="AB Coauthors", family="paragraph")

    coauthors_style.addElement(TextProperties(fontsize="12pt",
                                              fontstyle="italic"))

    odt.styles.addElement(coauthors_style)

    description_style = Style(name="AB Description", family="paragraph")

    description_style.addElement(TextProperties(fontsize="12pt"))

    odt.styles.addElement(description_style)

    footnotes_style = Style(name="AB Footnotes", family="paragraph")

    footnotes_style.addElement(TextProperties(fontsize="12pt"))

    odt.styles.addElement(footnotes_style)

    funding_agency_style = Style(name="AB Funding Agency", family="paragraph")

    funding_agency_style.addElement(TextProperties(fontsize="12pt"))

    odt.styles.addElement(funding_agency_style)

    return dict(
        rt=root_style,
        h1=h1_style,
        h2=h2_style,
        h3=h3_style,
        h4=title_style,
        h5=authors_style,
        h6=speakers_style,
        h7=coauthors_style,
        de=description_style,
        fn=footnotes_style,
        fa=funding_agency_style,
    )


def _abstract_booklet_chapters(odt: OpenDocument, ab: dict, styles: dict, settings: dict):
    """ Sessions """

    for session in ab.get('sessions', list()):

        ab_session_h1 = settings.get('ab_session_h1', '')
        ab_session_h2 = settings.get('ab_session_h2', '')
        ab_contribution_h1 = settings.get('ab_contribution_h1', '')
        ab_contribution_h2 = settings.get('ab_contribution_h2', '')

        print(">", session.get('code'), ' - ', session.get('title'), ' - ',
              session.get('start'), ' - ', session.get('end'))

        session_code = f"{session.get('code')}"
        session_title = f"{session.get('title')}"

        session_start = format_datetime_full(session.get('start'))
        session_end = format_datetime_time(session.get('end'))

        session_h1 = ab_session_h1 \
            .replace("{code}", session_code) \
            .replace("{title}", session_title) \
            .replace("{start}", session_start) \
            .replace("{end}", session_end)

        session_h2 = ab_session_h2 \
            .replace("{code}", session_code) \
            .replace("{title}", session_title) \
            .replace("{start}", session_start) \
            .replace("{end}", session_end)

        odt.text.addElement(  # type: ignore
            P(stylename=styles.get('h1'), 
              text=f"{session_h1} / {session_h2}")
        )

        session_conveners = session.get('conveners', [])

        if len(session_conveners) > 0:

            session_chair = P(stylename=styles.get('h2'),
                              text=f"Chair: ")

            for convener in session_conveners:
                session_chair.addText(
                    f"{convener.get('first')} {convener.get('last')} ({convener.get('affiliation')})"
                )

            odt.text.addElement(  # type: ignore
                session_chair
            )

        # Black line
        odt.text.addElement(P())  # type: ignore

        for contribution in session.get('contributions'):

            print()
            print("--- " + contribution.get('code'), ' - ', contribution.get('title'),' - ', 
                  contribution.get('start'), ' - ', contribution.get('end'))
            print()

            contribution_code = contribution.get('code')
            contribution_title = contribution.get('title')

            contribution_start = format_datetime_time(
                contribution.get('start'))
            contribution_end = format_datetime_time(
                contribution.get('end'))

            contribution_h1 = ab_contribution_h1 \
                .replace("{code}", contribution_code) \
                .replace("{title}", contribution_title) \
                .replace("{start}", contribution_start) \
                .replace("{end}", contribution_end)

            contribution_h2 = ab_contribution_h2 \
                .replace("{code}", contribution_code) \
                .replace("{title}", contribution_title) \
                .replace("{start}", contribution_start) \
                .replace("{end}", contribution_end)

            contribution_header = contribution_h1 if not \
                session.get('is_poster') else contribution_h2

            odt.text.addElement(  # type: ignore
                P(stylename=styles.get('h3'),
                    text=contribution_header)
            )

            odt.text.addElement(  # type: ignore
                P(stylename=styles.get('h4'),
                    text=f"{contribution.get('title')}")
            )


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

            if contribution_primary_authors_groups:

                contribution_primary_authors_para = P(
                    stylename=styles.get('h5'))

                for group_idx, group in enumerate(contribution_primary_authors_groups):
                    for item_idx, item in enumerate(group.get('items', [])):

                        # print(item.get('id'), contribution_speakers_ids, (int(item.get('id')) in contribution_speakers_ids))

                        stylename = styles.get('h6') if int(
                            item.get('id')) in contribution_speakers_ids else None

                        separator = "" if group_idx == len(
                            contribution_primary_authors_groups) - 1 else ", "

                        affiliation = f" ({item.get('affiliation')})" if item.get(
                            'affiliation') != '' else ''

                        text = f"{item.get('first', '')} {item.get('last')}" + affiliation \
                            if item_idx == len(group.get('items', []))-1 \
                            else f"{item.get('first')} {item.get('last')}"

                        contribution_primary_authors_para.addElement(  # type: ignore
                            Span(stylename=stylename, text=text)
                        )

                        contribution_primary_authors_para.addElement(  # type: ignore
                            Span(text=separator)
                        )

                odt.text.addElement(  # type: ignore
                    contribution_primary_authors_para
                )

            if contribution_coauthors_groups:

                contribution_coauthors_para = P(stylename=styles.get('h7'))

                for group_idx, group in enumerate(contribution_coauthors_groups):
                    for item_idx, item in enumerate(group.get('items', [])):

                        separator = "" if group_idx == len(
                            contribution_coauthors_groups) - 1 else ", "

                        affiliation = f" ({item.get('affiliation')})" if item.get(
                            'affiliation') != '' else ''

                        text = f"{item.get('first', '')} {item.get('last')}" + affiliation \
                            if item_idx == len(group.get('items', []))-1 \
                            else f"{item.get('first')} {item.get('last')}"

                        contribution_coauthors_para.addElement(  # type: ignore
                            Span(text=text)
                        )

                        contribution_coauthors_para.addElement(  # type: ignore
                            Span(text=separator)
                        )

                odt.text.addElement(  # type: ignore
                    contribution_coauthors_para
                )

            # Black line
            odt.text.addElement(P())  # type: ignore

            # print("--- " + contribution.get('description'),
            #       contribution.get('field_values'),
            #       settings.get('custom_fields'))

            # Description
            description_lines = contribution.get(
                'description', '').splitlines()

            for line in description_lines:
                odt.text.addElement(  # type: ignore
                    P(stylename=styles.get('de'),
                        text=f"{line}")
                )

            # Black line
            odt.text.addElement(P())  # type: ignore

            # Custom fields
            custom_fields = [
                f.get('name', None)
                for f in settings.get('custom_fields', list())
                if f.get('name', None)
            ]

            field_values = contribution.get('field_values', list())

            for field in field_values:

                if field.get('name', '') in custom_fields:
                    field_lines = field.get('value', '').splitlines()

                    for field_line in field_lines:
                        odt.text.addElement(  # type: ignore
                            P(stylename=styles.get('fn'),
                                text=f"{field_line}")
                        )

                    # Black line
                    odt.text.addElement(P())  # type: ignore

    return odt


def export_abstract_booklet_to_odt(ab: dict, event: dict, cookies: dict, settings: dict) -> io.BytesIO:
    """ """

    # 'application/vnd.oasis.opendocument.text'
    odt: OpenDocument = OpenDocumentText()

    styles = _document_styles(odt)

    # abstract_booklet_document = _abstract_booklet_index(abstract_booklet_document,
    #                                                        abstract_booklet_data,
    #                                                        heading_styles)

    odt = _abstract_booklet_chapters(odt, ab, styles, settings)

    return _serialize_abstract_booklet(odt)
