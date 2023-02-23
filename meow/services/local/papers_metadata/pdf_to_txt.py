import logging as lg

from fitz import Document
from io import StringIO, open


logger = lg.getLogger(__name__)


def pdf_to_txt(doc: Document) -> str:
    """ """

    out = StringIO()

    try:

        try:

            for page in doc:  # iterate the document pages
                text = page.get_textpage().extractText()  # get plain text (is in UTF-8)
                out.write(text)  # write text of page

        except Exception as e:
            logger.error(e, exc_info=True)

        doc.close()

    except Exception as e:
        logger.error(e, exc_info=True)

    return out.getvalue()
