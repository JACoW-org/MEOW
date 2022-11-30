import io
import logging as lg
import ulid

from itertools import groupby
from operator import itemgetter

# from PyRTF.Elements import Document
# from PyRTF.Renderer import Renderer
# from PyRTF.document.section import Section
from odf.opendocument import OpenDocumentText, OpenDocument
from odf.style import Style, TextProperties, ParagraphProperties

from odf.text import H, A, Span, P, HiddenParagraph, HiddenText, SoftPageBreak
from odf.text import TableOfContent, TableOfContentSource, TableOfContentEntryTemplate
from odf.text import IndexBody, IndexTitle, IndexEntryLinkStart, IndexEntryChapter, \
    IndexEntryPageNumber, IndexEntryText, IndexEntryLinkEnd, IndexTitleTemplate, \
    IndexEntryTabStop, IndexEntrySpan, Tab, BookmarkStart, BookmarkEnd, BookmarkRef

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

    bkm_style = Style(name="AB Bookmark", family="paragraph")

    bkm_style.addElement(TextProperties(fontsize="12pt"))

    odt.styles.addElement(bkm_style)

    idx_style = Style(name="AB Index", family="paragraph")

    idx_style.addElement(TextProperties(fontsize="12pt"))

    odt.styles.addElement(idx_style)

    hidden_style = Style(name="AB Hidden", family="paragraph")

    odt.styles.addElement(hidden_style)

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
        idx=idx_style,
        bkm=bkm_style,
        hid=hidden_style,
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


def _abstract_booklet_titles(ab: dict):
    """ Index """

    idx = dict()

    for session in ab.get('sessions', list()):

        print(">", session.get('code'), ' - ', session.get('title'), ' - ',
              session.get('start'), ' - ', session.get('end'))

        idx[session.get('code')] = dict(
            uuid=str(ulid.ULID()),
            code=session.get('code'),
            title=session.get('title')
        )

        for contribution in session.get('contributions'):

            idx[contribution.get('code')] = dict(
                uuid=str(ulid.ULID()),
                code=contribution.get('code'),
                title=contribution.get('title')
            )

    return idx


def _abstract_booklet_index(odt: OpenDocument, ab: dict, styles: dict, idx: dict):
    """ Index """

    odt_toc = TableOfContent(name="Table of Contents", protected=True)

    # <text:table-of-content-source text:outline-level="3">
    odt_tocs = TableOfContentSource(outlinelevel=3)

    # <text:index-title-template text:style-name="Contents_20_Heading">
    odt_itt = IndexTitleTemplate()
    odt_itt.addText("Table of Contents")

    # <text:table-of-content-entry-template text:outline-level="1" text:style-name="Contents_20_1">
    #     <text:index-entry-link-start text:style-name="Index_20_Link" />
    #     <text:index-entry-chapter />
    #     <text:index-entry-text />
    #     <text:index-entry-tab-stop style:type="right" style:leader-char="." />
    #     <text:index-entry-page-number />
    #     <text:index-entry-link-end />
    # </text:table-of-content-entry-template>

    # h1

    odt_toc_et_1 = TableOfContentEntryTemplate(
        outlinelevel=1, stylename=styles.get('idx'))

    idx_entry_link_start = IndexEntryLinkStart()
    idx_entry_link_chapter = IndexEntryChapter()
    idx_entry_link_text = IndexEntryText()
    idx_entry_link_tab_stop = IndexEntryTabStop(type="right", leaderchar=".")
    idx_entry_link_page_num = IndexEntryPageNumber()
    idx_entry_link_end = IndexEntryLinkEnd()

    odt_toc_et_1.addElement(idx_entry_link_start)
    # odt_toc_et_1.addElement(idx_entry_link_chapter)
    odt_toc_et_1.addElement(idx_entry_link_text)
    odt_toc_et_1.addElement(idx_entry_link_tab_stop)
    odt_toc_et_1.addElement(idx_entry_link_page_num)
    odt_toc_et_1.addElement(idx_entry_link_end)

    odt_tocs.addElement(odt_toc_et_1)

    # h2

    odt_toc_et_2 = TableOfContentEntryTemplate(
        outlinelevel=2, stylename=styles.get('idx'))

    idx_entry_link_start = IndexEntryLinkStart()
    idx_entry_link_chapter = IndexEntryChapter()
    idx_entry_link_text = IndexEntryText()
    idx_entry_link_span = IndexEntrySpan()
    idx_entry_link_tab_stop = IndexEntryTabStop(type="right", leaderchar=".")
    idx_entry_link_page_num = IndexEntryPageNumber()
    idx_entry_link_end = IndexEntryLinkEnd()

    odt_toc_et_2.addElement(idx_entry_link_start)
    # odt_toc_et_2.addElement(idx_entry_link_chapter)
    odt_toc_et_2.addElement(idx_entry_link_text)
    # odt_toc_et_2.addElement(idx_entry_link_span)
    # odt_toc_et_2.addElement(idx_entry_link_tab_stop)
    # odt_toc_et_2.addElement(idx_entry_link_page_num)
    odt_toc_et_2.addElement(idx_entry_link_end)

    odt_tocs.addElement(odt_toc_et_2)

    # h3

    odt_toc_et_3 = TableOfContentEntryTemplate(
        outlinelevel=3, stylename=styles.get('idx'))

    idx_entry_link_start = IndexEntryLinkStart()
    idx_entry_link_chapter = IndexEntryChapter()
    idx_entry_link_text = IndexEntryText()
    idx_entry_link_tab_stop = IndexEntryTabStop(type="right", leaderchar=".")
    idx_entry_link_page_num = IndexEntryPageNumber()
    idx_entry_link_end = IndexEntryLinkEnd()

    odt_toc_et_3.addElement(idx_entry_link_start)
    # odt_toc_et_3.addElement(idx_entry_link_chapter)
    odt_toc_et_3.addElement(idx_entry_link_text)
    odt_toc_et_3.addElement(idx_entry_link_tab_stop)
    odt_toc_et_3.addElement(idx_entry_link_page_num)
    odt_toc_et_3.addElement(idx_entry_link_end)

    odt_tocs.addElement(odt_toc_et_3)

    # title

    odt_tocs.addElement(odt_itt)

    odt_toc.addElement(odt_tocs)

    index_title = IndexTitle(name="Table of Contents",
                             stylename=styles.get('idx'))
    index_title.addElement(P(text="Table of Contents"))

    index_body = IndexBody()
    index_body.addElement(index_title)

    # for session in ab.get('sessions', list()):
    #
    #     print(">", session.get('code'), ' - ', session.get('title'), ' - ',
    #           session.get('start'), ' - ', session.get('end'))
    #
    #     session_idx = idx.get(session.get('code'), dict())
    #
    #     session_entry = P()
    #
    #     session_link = A(type="simple", href=f"#{session_idx.get('uuid')}")
    #
    #     session_link.addText(
    #         f"{session_idx.get('code')} - {session_idx.get('title')}")
    #     session_link.addElement(Tab())
    #     session_link.addText(f"1")
    #
    #     session_entry.addElement(session_link)
    #
    #     index_body.addElement(session_entry)
    #
    #     for contribution in session.get('contributions'):
    #
    #         contribution_idx = idx.get(contribution.get('code'), dict())
    #
    #         contribution_entry = P()
    #
    #         contribution_link = A(
    #             type="simple", href=f"#{session_idx.get('uuid')}")
    #
    #         contribution_link.addText(
    #             f"{contribution_idx.get('code')} - {contribution_idx.get('title')}")
    #         contribution_link.addElement(Tab())
    #         contribution_link.addText(f"1")
    #
    #         contribution_entry.addElement(contribution_link)
    #
    #         index_body.addElement(contribution_entry)

    odt_toc.addElement(index_body)

    odt.text.addElement(odt_toc)  # type: ignore

    odt.text.addElement(SoftPageBreak())  # type: ignore

    return odt


def _abstract_booklet_chapters(odt: OpenDocument, ab: dict, styles: dict, idx: dict, settings: dict):
    """ Sessions """

    ab_session_h1 = settings.get('ab_session_h1', '')
    ab_session_h2 = settings.get('ab_session_h2', '')
    ab_contribution_h1 = settings.get('ab_contribution_h1', '')
    ab_contribution_h2 = settings.get('ab_contribution_h2', '')

    for session in ab.get('sessions', list()):

        print(">", session.get('code'), ' - ', session.get('title'), ' - ',
              session.get('start'), ' - ', session.get('end'))

        session_code = f"{session.get('code')}"
        session_title = f"{session.get('title')}"

        session_start = format_datetime_full(session.get('start'))
        session_end = format_datetime_time(session.get('end'))

        session_idx = idx[session_code]

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

        # <text:bookmark-start text:name="__RefHeading___Toc8109_2226614992" />
        #     MOA - First lasing
        # <text:bookmark-end text:name="__RefHeading___Toc8109_2226614992" />

        session_bookmark = H(outlinelevel=1, stylename=styles.get('h1'))

        session_bookmark.addElement(
            BookmarkStart(name=session_idx.get('uuid')))
        session_bookmark.addText(session_h1)
        session_bookmark.addElement(BookmarkEnd(name=session_idx.get('uuid')))

        odt.text.addElement(  # type: ignore
            session_bookmark
        )

        odt.text.addElement(  # type: ignore
            P(stylename=styles.get('h2'), text=session_h2)
        )

        session_conveners = session.get('conveners', [])

        if len(session_conveners) > 0:

            session_chair = P(stylename=styles.get('h2'), text="Chair: ")

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
            print(">>> " + contribution.get('code'), ' - ', contribution.get('title'), ' - ',
                  contribution.get('start'), ' - ', contribution.get('end'))
            print()

            contribution_code = contribution.get('code')
            contribution_title = contribution.get('title')

            contribution_idx = idx.get(contribution_code, dict())

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

            # contribution_outline = H(outlinelevel=2, stylename=styles.get('hid'))
            # contribution_outline.addElement(
            #     Span(text=f"{contribution_code} - {contribution_title}")
            # )

            # , stylename=styles.get('bkm')

            contribution_bookmark = H(outlinelevel=3, stylename=styles.get('h4'))

            contribution_bookmark.addElement(
                BookmarkStart(name=contribution_idx.get('uuid')))
            contribution_bookmark.addText(contribution_title)
            contribution_bookmark.addElement(
                BookmarkEnd(name=contribution_idx.get('uuid')))

            contribution_h1 = H(outlinelevel=2, stylename=styles.get('h3'))

            contribution_h1.addElement(Span(text=contribution_code))
            contribution_h1.addText(" / ")
            contribution_h1.addText(text=contribution_start)

            odt.text.addElement(  # type: ignore
                contribution_h1
            )

            # odt.text.addElement(  # type: ignore
            #     P(stylename=styles.get('h3'), text=contribution_start)
            # )

            odt.text.addElement(  # type: ignore
                contribution_bookmark
            )

            # odt.text.addElement(  # type: ignore
            #     H(outlinelevel=3, stylename=styles.get(
            #         'h4'), text=contribution_title)
            # )

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

    idx = _abstract_booklet_titles(ab)

    odt = _abstract_booklet_index(odt, ab, styles, idx)

    odt = _abstract_booklet_chapters(odt, ab, styles, idx, settings)

    return _serialize_abstract_booklet(odt)
