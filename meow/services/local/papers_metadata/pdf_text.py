from typing import Any
from fitz import (TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT,
                  TEXT_ALIGN_JUSTIFY, Page, Rect)
from fitz.utils import getColor, insert_image, insert_textbox

PAGE_HORIZONTAL_MARGIN = 57
PAGE_VERTICAL_MARGIN = 15
LINE_SPACING = 3
ANNOTATION_HEIGHT = 15
SIDENOTE_LENGTH = 650
TEXT_COLOR = getColor('GRAY10')
FONT_SIZE = 7
# FONT_NAME = 'notos'
FONT_NAME = 'helv'


def write_page_header(page: Page, data: dict, options: dict = dict()):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN

    # top line

    # left
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
    #     align=TEXT_ALIGN_LEFT,
    #     text=data.get('series', 'Series'),
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(page=page,
                   rect=Rect(PAGE_HORIZONTAL_MARGIN,
                             PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width,
                             PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
                   align=TEXT_ALIGN_LEFT,
                   buffer=data.get('series', 'Series'),
                   fontname=options.get('fontName', FONT_NAME),
                   fontsize=options.get('fontSize', FONT_SIZE),
                   color=options.get('textColor', TEXT_COLOR),
                   )

    # middle
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN +
    #               rect_width,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
    #     align=TEXT_ALIGN_CENTER,
    #     text=data.get('venue', 'Code, Location'),
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_CENTER,
        buffer=data.get('venue', 'Code, Location'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # right
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN +
    #               rect_width,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
    #     align=TEXT_ALIGN_RIGHT,
    #     text=data.get('publisher', 'JACoW Publishing'),
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN +
                  rect_width,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_RIGHT,
        buffer=data.get('publisher', 'JACoW Publishing'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # bottom line

    # left
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
    #     align=TEXT_ALIGN_LEFT,
    #     text=f"ISBN: {data.get('isbn', 'isbn')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        buffer=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # middle
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
    #     align=TEXT_ALIGN_CENTER,
    #     text=f"ISSN: {data.get('issn', 'issn')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_CENTER,
        buffer=f"ISSN: {data.get('issn', 'issn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # right
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
    #     align=TEXT_ALIGN_RIGHT,
    #     text=f"doi: {data.get('doi', 'doi')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        buffer=f"doi: {data.get('doi', 'doi')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )


def write_page_footer(page: Page, page_number: int, data: dict, options: dict = dict()):
    """ """

    rect_width = page.mediabox.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.mediabox.height

    # bottom line

    # left
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               page_height - PAGE_VERTICAL_MARGIN),
    #     align=TEXT_ALIGN_LEFT,
    #     text=f"{page_number if page_number % 2 != 1 else data.get('classificationHeader', 'Classification Header')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_LEFT,
        buffer=str(page_number if page_number % 2 != 1 else data.get(
            'classificationHeader', 'Classification Header')),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # right
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               page_height - PAGE_VERTICAL_MARGIN),
    #     align=TEXT_ALIGN_RIGHT,
    #     text=f"{data.get('classificationHeader', 'Classification Header') if page_number % 2 != 1 else page_number}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_RIGHT,
        buffer=str(data.get('classificationHeader', 'Classification Header')
                   if page_number % 2 != 1 else page_number),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # top line

    # left
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
    #     align=TEXT_ALIGN_LEFT,
    #     text=f"{data.get('contributionCode', 'Contribution Code') if page_number % 2 != 1 else
    #       data.get('sessionHeader', 'Session Header')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        buffer=str(data.get('contributionCode', 'Contribution Code') if page_number %
                   2 != 1 else data.get('sessionHeader', 'Session Header')),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )

    # right
    # page.add_freetext_annot(
    #     rect=Rect(PAGE_HORIZONTAL_MARGIN,
    #               page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
    #               PAGE_HORIZONTAL_MARGIN + rect_width,
    #               page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
    #     align=TEXT_ALIGN_RIGHT,
    #     text=f"{data.get('sessionHeader', 'Session Header') if page_number % 2 != 1
    #          else data.get('contributionCode', 'Contribution Code')}",
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR)
    # )

    insert_textbox(
        page=page,
        rect=Rect(PAGE_HORIZONTAL_MARGIN,
                  page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING,
                  PAGE_HORIZONTAL_MARGIN + rect_width,
                  page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        buffer=str(data.get('sessionHeader', 'Session Header') if page_number %
                   2 != 1 else data.get('contributionCode', 'Contribution Code')),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR)
    )


def write_page_side(page: Page,
                    pre_print: str | None,
                    page_number: int | None,
                    license_icon: Any | None,
                    license_text: str,
                    options: dict = dict()):
    """ """

    page_width = page.mediabox.width
    page_height = page.mediabox.height

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
    if license_icon:
        insert_image(
            page=page,
            rect=rect_even_logo if page_number and page_number % 2 == 0 else rect_odd_logo,
            # filename='cc_by.png',
            rotate=90,
            stream=license_icon
        )

    # add copyright text
    # page.add_freetext_annot(
    #     rect=rect_even_text if page_number and page_number % 2 == 0 else rect_odd_text,
    #     align=TEXT_ALIGN_JUSTIFY,
    #     rotate=90,
    #     text='Content from this work may be used under the terms of the CC BY 4.0 licence (© 2022). ' +
    #          'Any distribution of this work must maintain attribution to the author(s), ' +
    #          'title of the work, publisher, and DOI.',
    #     fontname=options.get('fontName', FONT_NAME),
    #     fontsize=options.get('fontSize', FONT_SIZE),
    #     text_color=options.get('textColor', TEXT_COLOR),
    # )

    insert_textbox(
        page=page,
        rect=rect_even_text if page_number and page_number % 2 == 0 else rect_odd_text,
        align=TEXT_ALIGN_JUSTIFY,
        rotate=90,
        buffer='Content from this work may be used under the terms of the CC BY 4.0 licence (© 2022). ' +
        'Any distribution of this work must maintain attribution to the author(s), ' +
        'title of the work, publisher, and DOI.',
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        color=options.get('textColor', TEXT_COLOR),
    )

    if pre_print:

        # add pre print
        # page.add_freetext_annot(
        #     rect=rect_even_text if page_number and page_number % 2 != 0 else rect_odd_text,
        #     align=TEXT_ALIGN_JUSTIFY,
        #     rotate=90,
        #     text=pre_print,
        #     # fontname=options.get('fontName', FONT_NAME),
        #     fontsize=options.get('fontSize', FONT_SIZE),
        #     text_color=options.get('textColor', TEXT_COLOR),
        # )

        # font = Font('cjk')

        # page.insert_font(fontname='cjk', fontbuffer=font.buffer)

        insert_textbox(
            page=page,
            rect=rect_even_text if page_number and page_number % 2 != 0 else rect_odd_text,
            align=TEXT_ALIGN_JUSTIFY,
            rotate=90,
            buffer=pre_print,
            fontname=options.get('fontName', FONT_NAME),
            fontsize=options.get('fontSize', FONT_SIZE),
            color=options.get('textColor', TEXT_COLOR),
        )
