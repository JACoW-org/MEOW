from fitz import (Document, Page, Font)


FONT_NAME = 'notos'


def insert_notos_font(doc: Document, page: Page):
    notos: bool = False

    for font in page.get_fonts(True):
        if notos is False:
            extraction = doc.extract_font(font[0])
            notos = extraction[0] == 'notos' # type: ignore

    if notos is False:
        page.insert_font(fontname=FONT_NAME, fontbuffer=Font(FONT_NAME).buffer)
