from typing import Any
from fitz import (Page, Rect, TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER,
                  TEXT_ALIGN_RIGHT, TEXT_ALIGN_JUSTIFY)
from fitz.utils import getColor, insert_image


PAGE_HORIZONTAL_MARGIN = 57
PAGE_VERTICAL_MARGIN = 15
LINE_SPACING = 3
ANNOTATION_HEIGHT = 10
SIDENOTE_LENGTH = 650
TEXT_COLOR = getColor('GRAY10')
FONT_SIZE = 7
# FONT_NAME = 'notos'
FONT_NAME = None


def annot_toc_header(page: Page, data: dict, options: dict = dict()):
    """ """

    # header = dict(
    #     name=proceedings_data.event.name,
    #     series=proceedings_data.event.series,
    #     location=proceedings_data.event.location,
    #     date=proceedings_data.event.date,
    #     isbn=proceedings_data.event.isbn,
    #     doi=proceedings_data.event.doi_label,
    #     issn=proceedings_data.event.issn,
    # )

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN,
                  PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_LEFT,
        text='',
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN,
                  PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_CENTER,
        text=data.get('title', 'Title'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN,
                  PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_RIGHT,
        text=data.get('publisher', 'JACoW Publishing'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        text=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_CENTER,
        text=f"ISSN: {data.get('issn', 'issn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        text=f"doi: {data.get('doi', 'doi')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )


def annot_page_header(page: Page, data: dict, options: dict = dict()):
    """ """

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN,
                  PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_LEFT,
        text=data.get('series', 'Series'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_CENTER,
        text=data.get('venue', 'Code, Location'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN,
                  PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_RIGHT,
        text=data.get('publisher', 'JACoW Publishing'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        text=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_CENTER,
        text=f"ISSN: {data.get('issn', 'issn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        text=f"doi: {data.get('doi', 'doi')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )


def annot_toc_footer(page: Page, page_number: int, data: dict, options: dict = dict()):
    """ """

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.rect.height

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_LEFT,
        text=f"{intToRoman(page_number) if page_number % 2 != 1 else data.get('name', '')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_RIGHT,
        text=f"{data.get('name', '') if page_number % 2 != 1 else intToRoman(page_number)}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )


def annot_page_footer(page: Page, page_number: int, data: dict, options: dict = dict()):
    ''''''

    sess_header = data.get('sessionHeader', 'Session Header')
    contrib_code = data.get('contributionCode', 'Contribution Code')
    track_header = data.get('classificationHeader', 'Classification Header')

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.rect.height

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_LEFT,
        text=f"{page_number if page_number % 2 != 1 else track_header}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_RIGHT,
        text=f"{track_header if page_number % 2 != 1 else page_number}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        text=f"{contrib_code if page_number % 2 != 1 else sess_header}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        text=f"{sess_header if page_number % 2 != 1 else contrib_code}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR)
    )


def annot_page_side(page: Page,
                    pre_print: str | None,
                    page_number: int | None,
                    cc_logo: Any | None,
                    options: dict = dict()):

    page_width = page.rect.width
    page_height = page.rect.height

    rect_even_logo = Rect(
        PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 15,
        PAGE_HORIZONTAL_MARGIN / 2 + ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2
    )

    rect_even_text = Rect(
        PAGE_HORIZONTAL_MARGIN / 2 + 1,
        page_height / 2 - SIDENOTE_LENGTH / 2,
        PAGE_HORIZONTAL_MARGIN / 2 + ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 16
    )

    rect_odd_logo = Rect(
        page_width - PAGE_HORIZONTAL_MARGIN / 2 - ANNOTATION_HEIGHT,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 15,
        page_width - PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2
    )

    rect_odd_text = Rect(
        page_width - PAGE_HORIZONTAL_MARGIN / 2 - ANNOTATION_HEIGHT + 1,
        page_height / 2 - SIDENOTE_LENGTH / 2,
        page_width - PAGE_HORIZONTAL_MARGIN / 2,
        page_height / 2 + SIDENOTE_LENGTH / 2 - 16
    )

    # add cc logo
    insert_image(
        page=page,
        rect=rect_even_logo if page_number and page_number % 2 == 0 else rect_odd_logo,
        # filename='cc_by.png',
        rotate=90,
        stream=cc_logo
    )

    # add copyright text
    page.add_freetext_annot(
        rect=rect_even_text if page_number and page_number % 2 == 0 else rect_odd_text,
        align=TEXT_ALIGN_JUSTIFY,
        rotate=90,
        text='Content from this work may be used under the terms of the CC BY 4.0 licence (© 2022). ' +
             'Any distribution of this work must maintain attribution to the author(s), ' +
             'title of the work, publisher, and DOI.',
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get('textColor', TEXT_COLOR),
    )

    if pre_print:

        # add pre print
        page.add_freetext_annot(
            rect=rect_even_text if page_number and page_number % 2 != 0 else rect_odd_text,
            align=TEXT_ALIGN_JUSTIFY,
            rotate=90,
            text=pre_print,
            # fontname=options.get('fontName', FONT_NAME),
            fontsize=options.get('fontSize', FONT_SIZE),
            text_color=options.get('textColor', TEXT_COLOR),
        )


def intToRoman(num: int) -> str:

    # Storing roman values of digits from 0-9
    # when placed at different places
    m = ["", "M", "MM", "MMM"]
    c = ["", "C", "CC", "CCC", "CD", "D",
         "DC", "DCC", "DCCC", "CM "]
    x = ["", "X", "XX", "XXX", "XL", "L",
         "LX", "LXX", "LXXX", "XC"]
    i = ["", "I", "II", "III", "IV", "V",
         "VI", "VII", "VIII", "IX"]

    # Converting to roman
    thousands = m[num // 1000]
    hundreds = c[(num % 1000) // 100]
    tens = x[(num % 100) // 10]
    ones = i[num % 10]

    ans = (thousands + hundreds +
           tens + ones)

    return ans
