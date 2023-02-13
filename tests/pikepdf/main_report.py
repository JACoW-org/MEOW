"""

Esecuzione parallela all'interno di un task group

"""

import io

from typing import List, Optional
from dataclasses import dataclass

from anyio import create_task_group, CapacityLimiter

from fitz import Document

from meow.utils.http import download_stream


@dataclass
class PdfPageFontReport:
    name: Optional[str] = None
    type: Optional[str] = None
    ext: Optional[str] = None
    emb: Optional[bool] = None


@dataclass
class PdfPageSizeReport:
    width: float
    height: float


@dataclass
class PdfPageReport:
    sizes: PdfPageSizeReport


@dataclass
class PdfReport:
    page_count: int
    pages_report: List[PdfPageReport]
    fonts_report: List[PdfPageFontReport]


async def event_pdf_report(pdf_stream: io.BytesIO) -> PdfReport | None:
    """ """

    try:

        pdf = Document(stream=pdf_stream, filetype='pdf')

        try:

            page_count = 0
            pages_report = []
            fonts_report = []

            xref_list = []

            for page in pdf:
                page_count = page_count + 1

                for font in page.get_fonts(True):

                    xref = font[0]

                    if xref not in xref_list:

                        xref_list.append(xref)

                        font_name, font_ext, font_type, buffer = pdf.extract_font(
                            xref)
                        font_emb = (
                            font_ext == "n/a" or len(buffer) == 0) == False

                        # print("font_name", font_name, "font_emb", font_emb, "font_ext", font_ext, "font_type", font_type, len(buffer)) # font.name, font.flags, font.bbox, font.buffer

                        fonts_report.append(PdfPageFontReport(
                            name=font_name, emb=font_emb,
                            ext=font_ext, type=font_type))

                page_report = PdfPageReport(
                    sizes=PdfPageSizeReport(
                        width=page.mediabox_size.y,
                        height=page.mediabox_size.x
                    )
                )

                pages_report.append(page_report)

            fonts_report.sort(key=lambda x: x.name)

            return PdfReport(
                page_count=page_count,
                pages_report=pages_report,
                fonts_report=fonts_report
            )

        except Exception:
            pass

        pdf.close()

    except Exception as e:
        pass

    return None


async def main():

    SETTINGS = {
        "page_size_limit": "12x10",
        "page_count_limit": 300
    }

    PDF_FILE = {
        "url": "http://127.0.0.1:8005/event/12/contributions/2640/editing/paper/6059/17077/TUP22.pdf",
        "_url": "https://indico.jacow.org/event/44/contributions/349/attachments/227/751/AppleIII-Development_Tischer_FEL2022-THBI1.pdf",
        "_url": "https://vtechworks.lib.vt.edu/bitstream/handle/10919/73229/Base%2014%20Fonts.pdf?sequence=1&isAllowed=y",
        "name": "AppleIII-Development_Tischer_FEL2022-THBI1.pdf",
        "size": 4227793,
        "checksum": "1da86ed088b37886969d71876ac0ced6"
    }

    async def task(num: int, limiter: CapacityLimiter, file: dict):
        async with limiter:
            pdf_stream = await download_stream(file.get('url', None), headers=dict(
                Authorization="Bearer indp_9bjGQIZOeK7k19kXaiheF1tFLeSuhxvedChnPJgsbj"
            ))

            # if not file.get("checksum", None) == str(hashlib.md5(pdf_stream.getbuffer()).hexdigest()):
            #     raise Exception("invalid checksum")

            # /home/fabio.meneghetti/Documents/RichiestaMutuo.pdf

            # result = await to_process.run_sync(check_pdf, pdf_stream)
            result = await event_pdf_report(pdf_stream)
            
            if result is not None:

                print('## page_count:', result.page_count)

                for page_report in result.pages_report:

                    print('##', page_report.sizes)

                for font_report in result.fonts_report:

                    print('--', font_report)

    # await task()

    limiter = CapacityLimiter(20)
    async with create_task_group() as tg:
        for num in range(1):
            tg.start_soon(task, num, limiter, PDF_FILE)
            # await task(num, limiter, PDF_FILE)

    # result = await run_process('sleep 30')
    # print(result.stdout.decode())

    # check_pdf(pdf_stream)

    return None
