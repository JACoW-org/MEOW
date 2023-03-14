from fitz import Page, Rect, TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT
from fitz.utils import getColor
from meow.models.local.event.final_proceedings.contribution_model import ContributionData

PAGE_HORIZONTAL_MARGIN = 50
PAGE_VERTICAL_MARGIN = 15
LINE_SPACING = 3
ANNOTATION_HEIGHT = 10
TEXT_COLOR = getColor('GRAY10')
FONT_SIZE = 7
FONT_NAME = None

def annot_page_header(page: Page, data: dict, options: dict = dict()):
    ''''''
    rect_width = page.rect.width - 2* PAGE_HORIZONTAL_MARGIN

    # top line

    # left_
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_LEFT,
        text=data.get('series', 'Series'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_CENTER,
        text=data.get('venue', 'Code, Location'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
        align=TEXT_ALIGN_RIGHT,
        text=data.get('publisher', 'JACoW Publishing'),
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        text=f"ISBN: {data.get('isbn', 'isbn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # middle
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_CENTER,
        text=f"ISSN: {data.get('issn', 'issn')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT + LINE_SPACING, PAGE_HORIZONTAL_MARGIN + rect_width, PAGE_VERTICAL_MARGIN + 2 * ANNOTATION_HEIGHT + LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        text=f"doi: {data.get('doi', 'doi')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

def annot_page_footer(page: Page, page_number: int, data: dict, options: dict = dict()):
    ''''''

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN
    page_height = page.rect.height

    # bottom line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT, PAGE_HORIZONTAL_MARGIN + rect_width, page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_LEFT,
        text=f"{page_number if page_number % 2 != 1 else data.get('classificationHeader', 'Classification Header')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT, PAGE_HORIZONTAL_MARGIN + rect_width, page_height - PAGE_VERTICAL_MARGIN),
        align=TEXT_ALIGN_RIGHT,
        text=f"{data.get('classificationHeader', 'Classification Header') if page_number % 2 != 1 else page_number}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # top line

    # left
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING, PAGE_HORIZONTAL_MARGIN + rect_width, page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_LEFT,
        text=f"{data.get('contributionCode', 'Contribution Code') if page_number % 2 != 1 else data.get('sessionHeader', 'Session Header')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

    # right
    page.add_freetext_annot(
        rect=Rect(PAGE_HORIZONTAL_MARGIN, page_height - PAGE_VERTICAL_MARGIN - 2 * ANNOTATION_HEIGHT - LINE_SPACING, PAGE_HORIZONTAL_MARGIN + rect_width, page_height - PAGE_VERTICAL_MARGIN - ANNOTATION_HEIGHT - LINE_SPACING),
        align=TEXT_ALIGN_RIGHT,
        text=f"{data.get('sessionHeader', 'Session Header') if page_number % 2 != 1 else data.get('contributionCode', 'Contribution Code')}",
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )

def annot_page_side(page: Page, page_number: int, options: dict = dict()):

    page_width = page.rect.width
    page_height = page.rect.height

    rect_even = Rect(
        PAGE_HORIZONTAL_MARGIN / 2,
        PAGE_VERTICAL_MARGIN,
        PAGE_HORIZONTAL_MARGIN / 2 + ANNOTATION_HEIGHT,
        page_height - PAGE_VERTICAL_MARGIN
    )

    rect_odd = Rect(
        page_width - PAGE_HORIZONTAL_MARGIN / 2 - ANNOTATION_HEIGHT,
        PAGE_VERTICAL_MARGIN,
        page_width - PAGE_HORIZONTAL_MARGIN / 2,
        page_height - PAGE_VERTICAL_MARGIN
    )

    # TODO add image CC BY

    page.add_freetext_annot(
        rect=rect_even if page_number % 2 == 0 else rect_odd,
        align=TEXT_ALIGN_CENTER,
        rotate=90,
        text='Content from this work may be used under the terms of the CC BY 4.0 licence (© 2022). Any distribution of this work must maintain attribution to the author(s), title of the work, publisher, and DOI.',
        fontname=options.get('fontName', FONT_NAME),
        fontsize=options.get('fontSize', FONT_SIZE),
        text_color=options.get ('textColor', TEXT_COLOR)
    )
