
import logging as lg

from fitz import Document


logger = lg.getLogger(__name__)


def get_pdf_report(pdf: Document):

    try:

        pages_report = []
        fonts_report = []
        xref_list = []

        for page in pdf:

            for font in page.get_fonts(True):

                xref = font[0]

                if xref not in xref_list:

                    xref_list.append(xref)

                    extracted = pdf.extract_font(xref)
                    font_name, font_ext, font_type, buffer = extracted
                    font_emb = (font_ext == "n/a" or len(buffer) == 0) == False

                    # print("font_name", font_name, "font_emb", font_emb, "font_ext", font_ext, "font_type", font_type, len(buffer)) # font.name, font.flags, font.bbox, font.buffer

                    fonts_report.append(dict(
                        name=font_name, emb=font_emb,
                        ext=font_ext, type=font_type))

            page_report = dict(sizes=dict(
                width=page.mediabox_size.y,
                height=page.mediabox_size.x))

            pages_report.append(page_report)

        fonts_report.sort(key=lambda x: x.get('name'))

        return dict(
            page_count=pdf.page_count,
            pages_report=pages_report,
            fonts_report=fonts_report
        )

    except Exception as e:
        logger.error(e, exc_info=True)

