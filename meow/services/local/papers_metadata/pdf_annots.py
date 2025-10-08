from typing import Any

from fitz import (
    Page,
    Rect,
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_RIGHT,
    TEXT_ALIGN_JUSTIFY,
)

from fitz.utils import (
    getColor,
    insert_image,
)

from meow.fonts import (
    FiraGO_Regular as Helvetica_Regular,
    FiraMono_Regular as Courier_Regular,
    FiraMono_Bold as Courier_Bold,
)

from meow.services.local.papers_metadata.pdf_utils import intToRoman

PAGE_HORIZONTAL_MARGIN = 57
PAGE_VERTICAL_MARGIN = 15
LINE_SPACING = 3
ANNOTATION_HEIGHT = 10
SIDENOTE_LENGTH = 650

ANNOTS_FONT_SIZE = 7
ANNOTS_TEXT_COLOR = getColor("GRAY10")
ANNOTS_FONT_NAME = Helvetica_Regular.fontalias


def annot_toc_header(page: Page, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_LEFT,
        text="",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_CENTER,
        text=data.get("title", "Title"),
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=data.get("publisher", "JACoW Publishing"),
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        text=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_CENTER,
        text=f"ISSN: {data.get('issn', 'issn')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=f"doi: {data.get('doi', 'doi')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )


def annot_toc_footer(page: Page, page_number: int, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.mediabox.height

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_LEFT,
        text=f"{intToRoman(page_number) if page_number % 2 != 1 else data.get('name', '')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=f"{data.get('name', '') if page_number % 2 != 1 else intToRoman(page_number)}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )


def annot_page_header(page: Page, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_LEFT,
        text=data.get("series", "Series"),
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_CENTER,
        text=data.get("venue", "Code, Location"),
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=data.get("publisher", "JACoW Publishing"),
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        text=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_CENTER,
        text=f"ISSN: {data.get('issn', 'issn')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=f"doi: {data.get('doi', 'doi')}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )


def annot_page_footer(page: Page, page_number: int, data: dict):
    """"""

    sess_header = data.get("sessionHeader", "Session Header")
    contrib_code = data.get("contributionCode", "Contribution Code")
    track_header = data.get("classificationHeader", "Classification Header")

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.mediabox.height

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_LEFT,
        text=f"{page_number if page_number % 2 != 1 else track_header}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=f"{track_header if page_number % 2 != 1 else page_number}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        text=f"{contrib_code if page_number % 2 != 1 else sess_header}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    # right
    page.add_freetext_annot(
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        text=f"{sess_header if page_number % 2 != 1 else contrib_code}",
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )


def annot_page_side(
    page: Page,
    pre_print: str | None,
    page_number: int | None,
    license_icon: Any | None,
    license_text: str,
):
    """ """

    page_width = page.mediabox.width
    page_height = page.mediabox.height

    rect_even_logo = Rect(
        PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 15,
        PAGE_HORIZONTAL_MARGIN / 2 + ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2,
    )

    rect_even_text = Rect(
        PAGE_HORIZONTAL_MARGIN / 2 + 1,
        page_height / 2 - SIDENOTE_LENGTH / 2,
        PAGE_HORIZONTAL_MARGIN / 2 + ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 16,
    )

    rect_odd_logo = Rect(
        page_width - PAGE_HORIZONTAL_MARGIN / 2 - ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 15,
        page_width - PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2,
    )

    rect_odd_text = Rect(
        page_width - PAGE_HORIZONTAL_MARGIN / 2 - ANNOTATION_HEIGHT + 1,
        page_height / 2 - SIDENOTE_LENGTH / 2,
        page_width - PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 16,
    )

    # add cc logo
    insert_image(
        page=page,
        rect=rect_even_logo if page_number and page_number % 2 == 0 else rect_odd_logo,
        rotate=90,
        stream=license_icon,
    )

    # add copyright text
    page.add_freetext_annot(
        rect=rect_even_text if page_number and page_number % 2 == 0 else rect_odd_text,
        align=TEXT_ALIGN_JUSTIFY,
        rotate=90,
        text=license_text,
        fontname=ANNOTS_FONT_NAME,
        fontsize=ANNOTS_FONT_SIZE,
        text_color=ANNOTS_TEXT_COLOR,
    )

    if pre_print:
        # add pre print
        page.add_freetext_annot(
            rect=rect_even_text
            if page_number and page_number % 2 != 0
            else rect_odd_text,
            align=TEXT_ALIGN_JUSTIFY,
            rotate=90,
            text=pre_print,
            fontname=ANNOTS_FONT_NAME,
            fontsize=ANNOTS_FONT_SIZE,
            text_color=ANNOTS_TEXT_COLOR,
        )
