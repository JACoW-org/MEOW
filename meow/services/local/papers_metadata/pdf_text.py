from typing import Any
from fitz import (
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_RIGHT,
    TEXT_ALIGN_JUSTIFY,
    Page,
    Rect,
)

from fitz.utils import getColor, insert_image, insert_textbox

from meow.services.local.papers_metadata.pdf_utils import intToRoman

from meow.fonts import (
    FiraGO_Regular as Helvetica_Regular,
    FiraMono_Regular as Courier_Regular,
    FiraMono_Bold as Courier_Bold,
)

PAGE_HORIZONTAL_MARGIN = 57
PAGE_VERTICAL_MARGIN = 15
LINE_SPACING = 3
ANNOTATION_HEIGHT = 15
SIDENOTE_LENGTH = 650

TEXTBOX_FONT_SIZE = 7
TEXTBOX_TEXT_COLOR = getColor("GRAY10")
TEXTBOX_FONT_NAME = Helvetica_Regular.fontalias


def write_toc_header(page: Page, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer="",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # middle
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_CENTER,
        buffer=data.get("title", "Title"),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=data.get("publisher", "JACoW Publishing"),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # bottom line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # middle
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_CENTER,
        buffer=f"ISSN: {data.get('issn', 'issn')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=f"doi: {data.get('doi', 'doi')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )


def write_toc_footer(page: Page, page_number: int, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.mediabox.height

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=f"{intToRoman(page_number) if page_number % 2 != 1 else data.get('name', '')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=f"{data.get('name', '') if page_number % 2 != 1 else intToRoman(page_number)}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )


def write_page_header(page: Page, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=data.get("series", "Series"),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # middle
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_CENTER,
        buffer=data.get("venue", "Code, Location"),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=data.get("publisher", "JACoW Publishing"),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # bottom line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # middle
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_CENTER,
        buffer=f"ISSN: {data.get('issn', 'issn')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=f"doi: {data.get('doi', 'doi')}",
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )


def write_page_footer(page: Page, page_number: int, data: dict):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.mediabox.height

    # bottom line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=str(
            page_number
            if page_number % 2 != 1
            else data.get("classificationHeader", "Classification Header")
        ),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=str(
            data.get("classificationHeader", "Classification Header")
            if page_number % 2 != 1
            else page_number
        ),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # top line

    # left
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING,
        ),
        align=TEXT_ALIGN_LEFT,
        buffer=str(
            data.get("contributionCode", "Contribution Code")
            if page_number % 2 != 1
            else data.get("sessionHeader", "Session Header")
        ),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    # right
    insert_textbox(
        page=page,
        rect=Rect(
            PAGE_HORIZONTAL_MARGIN,
            page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
            PAGE_HORIZONTAL_MARGIN + rect_width,
            page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING,
        ),
        align=TEXT_ALIGN_RIGHT,
        buffer=str(
            data.get("sessionHeader", "Session Header")
            if page_number % 2 != 1
            else data.get("contributionCode", "Contribution Code")
        ),
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )


def write_page_side(
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
    if license_icon:
        insert_image(
            page=page,
            rect=rect_even_logo
            if page_number and page_number % 2 == 0
            else rect_odd_logo,
            # filename='cc_by.png',
            rotate=90,
            stream=license_icon,
        )

    # add copyright text
    insert_textbox(
        page=page,
        rect=rect_even_text if page_number and page_number % 2 == 0 else rect_odd_text,
        align=TEXT_ALIGN_JUSTIFY,
        rotate=90,
        buffer=license_text,
        fontname=TEXTBOX_FONT_NAME,
        fontsize=TEXTBOX_FONT_SIZE,
        color=TEXTBOX_TEXT_COLOR,
    )

    if pre_print:
        # add pre print
        insert_textbox(
            page=page,
            rect=rect_even_text
            if page_number and page_number % 2 != 0
            else rect_odd_text,
            align=TEXT_ALIGN_JUSTIFY,
            rotate=90,
            buffer=pre_print,
            fontname=TEXTBOX_FONT_NAME,
            fontsize=TEXTBOX_FONT_SIZE,
            color=TEXTBOX_TEXT_COLOR,
        )
