"""

Esecuzione parallela all'interno di un task group

"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from anyio import run_process, create_task_group, run, CapacityLimiter
from typing import Any

import sys
import io
import pathlib
import hashlib

from fitz import Document

from anyio import run, to_process
from anyio import open_file, run

# from pikepdf import open
# from pikepdf.objects import Object  # type: ignore
# from pikepdf.objects import Dictionary, String, Array, Stream

from meow.utils.http import download_stream


@dataclass
class PdfPageFontReport:
    name: Optional[str] = None
    enc: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    emb: Optional[bool] = None


@dataclass
class PdfPageSizeReport:
    width: float
    height: float


@dataclass
class PdfPageReport:
    sizes: PdfPageSizeReport
    fonts: Dict[str, PdfPageFontReport]


@dataclass
class PdfReport:
    page_count: int
    pages_report: List[PdfPageReport]


async def fill_font(key: str, value: Any, level: int, fonts: dict, font: PdfPageFontReport):
    """ """

    try:
        if level == 2 and key == '/BaseFont':
            font.name = str(value)
            fonts[font.name] = font

        if level == 2 and key == '/Encoding':
            font.enc = str(value)

        if level == 2 and key == '/Type':
            font.type = str(value)

        if level == 2 and key == '/Subtype':
            font.subtype = str(value)

        if level == 3 and key in ['/FontFile', '/FontFile2', '/FontFile3']:
            font.emb = True
    except:
        pass


async def load_font(key: str, value: Any, level: int, fonts: dict, font: PdfPageFontReport):
    """ """

    await fill_font(key, value, level, fonts, font)

    # print(level, " " * level, key, ":", type(value), font)

    if isinstance(value, Dictionary):
        for child_key, child_value in value.items():
            await load_font(child_key, child_value, level+1, fonts, font)


async def event_pdf_report(pdf_stream: io.BytesIO):
    """ """

    with open(pdf_stream) as p:

        result = PdfReport(page_count=len(p.pages), pages_report=[])

        # for key, value in p.docinfo.items():
        #     if key in ['/Title', '/Author', '/CreationDate', '/Creator', '/ModDate', '/Producer']:
        #         await load_meta(key, value, 0, result["meta"], {})

        for page in p.pages:

            fonts = dict()

            if isinstance(page.obj, Array):
                for i in page.obj.keys():
                    await load_font("", i, 0, fonts, PdfPageFontReport())
            else:
                for key, value in page.resources.items():
                    if key in ['/Font', '/FontFamily', '/FontName', '/Type', '/FontFile', '/FontFile2', '/FontFile3', '/Encoding', '/BaseFont', '/ToUnicode', '/DescendantFonts']:
                        await load_font(key, value, 0, fonts, PdfPageFontReport())

            if '/CropBox' in page:
                # use CropBox if defined since that's what the PDF viewer would usually display
                relevant_box = page.CropBox
            elif '/MediaBox' in page:
                relevant_box = page.MediaBox
            else:
                # fall back to ANSI A (US Letter) if neither CropBox nor MediaBox are defined
                # unlikely, but possible
                relevant_box = None

            # actually there could also be a viewer preference ViewArea or ViewClip in
            # pdf.Root.ViewerPreferences defining which box to use, but most PDF readers
            # disregard this option anyway

            # check whether the page defines a UserUnit
            userunit = 1
            if '/UserUnit' in page:
                userunit = float(page.UserUnit)  # type: ignore

            relevant_box = [
                float(x)*userunit
                for x in relevant_box  # type: ignore
            ]

            # obtain the dimensions of the box
            width = abs(relevant_box[2] - relevant_box[0])
            height = abs(relevant_box[3] - relevant_box[1])

            rotation = 0
            if '/Rotate' in page:
                rotation = page.Rotate

            # if the page is rotated clockwise or counter-clockwise, swap width and height
            # (pdf rotation modifies the coordinate system, so the box always refers to
            # the non-rotated page)
            if (rotation // 90) % 2 != 0:  # type: ignore
                width, height = height, width

            page_report = PdfPageReport(
                sizes=PdfPageSizeReport(
                    width=width,
                    height=height
                ),
                fonts=fonts
            )

            result.pages_report.append(page_report)

        p.close()

    pdf_stream.close()

    return result


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

            print('## page_count:', result.page_count)

            for page_report in result.pages_report:

                print('##', page_report.sizes)

                for font in page_report.fonts.values():
                    print('  --', font)

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
