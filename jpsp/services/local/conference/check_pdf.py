
import io
import logging as lg

from pikepdf import open
from pikepdf.objects import Dictionary, Array

from anyio import create_task_group, CapacityLimiter
from anyio import to_process, to_thread
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import (
    MemoryObjectReceiveStream,
    MemoryObjectSendStream,
    MemoryObjectStreamState,
)

from typing import Any, List, Dict, Optional
from dataclasses import dataclass, asdict

from jpsp.utils.http import download_stream


logger = lg.getLogger(__name__)


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


async def event_pdf_check(contributions: list[dict], cookies: dict = {}):
    """ """

    # logger.debug(f'event_pdf_check - count: {len(contributions)} - cookies: {cookies}')

    files = await extract_event_pdf_files(contributions)

    total_files: int = len(files)
    checked_files: int = 0

    # logger.debug(f'event_pdf_check - files: {len(files)}')

    send_reports_stream, receive_reports_stream = create_memory_object_stream()

    limiter = CapacityLimiter(6)

    async with create_task_group() as tg:
        async with send_reports_stream:
            for index, current in enumerate(files):
                tg.start_soon(_task, limiter, total_files, index,
                              current, cookies, send_reports_stream.clone())

        try:
            async with receive_reports_stream:
                async for report in receive_reports_stream:
                    checked_files = checked_files + 1
                    
                    # print('receive_reports_stream::report-->',
                    #       checked_files, total_files)

                    yield report

                    if checked_files >= total_files:
                        receive_reports_stream.close()
        except ClosedResourceError:
            pass


async def extract_event_pdf_files(elements: list[dict]) -> list:
    """ """

    files = []

    for element in elements:
        revisions = element.get('revisions', [])
        for file in revisions[-1].get('files', []):
            files.append(file)

        # for revision in element.get('revisions', []):
        #     for file in revision.get('files', []):
        #         files.append(file)

    return files


async def _task(l: CapacityLimiter, t: int, i: int, f: dict, c: dict, res: MemoryObjectSendStream):
    """ """

    if l is not None:
        async with l:
            await res.send({
                "index": i,
                "total": t,
                "file": f,
                "report": await _run(f, c)
            })
    else:
        await res.send({
            "file": f,
            "report": await _run(f, c)
        })


async def _run(f: dict, c: dict):
    """ """

    url = f.get('download_url', '')
    
    # logger.debug(f'_task: begin -> {url} -> {c}')

    # await sleep(15)
    #
    # logger.debug(f'_task: end -> {url}')
    #
    # return {}

    cookies = dict(indico_session_http=c.get('indico_session_http', ''))
    pdf_stream = await download_stream(f.get('external_download_url', ''), cookies=cookies)

    # print(l.total_tokens)

    return await to_thread.run_sync(event_pdf_report, pdf_stream)
    # return await to_process.run_sync(event_pdf_report, pdf_stream)
    # return event_pdf_report(pdf_stream)


def event_pdf_report(pdf_stream: io.BytesIO):
    """ """

    try:

        with open(pdf_stream) as p:

            result = PdfReport(page_count=len(p.pages), pages_report=[])

            # for key, value in p.docinfo.items():
            #     if key in ['/Title', '/Author', '/CreationDate', '/Creator', '/ModDate', '/Producer']:
            #         load_meta(key, value, 0, result["meta"], {})

            for page in p.pages:

                fonts = dict()

                if isinstance(page.obj, Array):
                    for i in page.obj.keys():
                        load_font("", i, 0, fonts, PdfPageFontReport())
                else:
                    for key, value in page.resources.items():
                        if key in ['/Font', '/FontFamily', '/FontName', '/Type', '/FontFile', '/FontFile2', '/FontFile3', '/Encoding', '/BaseFont', '/ToUnicode', '/DescendantFonts']:
                            load_font(key, value, 0, fonts,
                                      PdfPageFontReport())

                if '/CropBox' in page:
                    # use CropBox if defined since that's what the PDF viewer would usually display
                    relevant_box = page.CropBox
                elif '/MediaBox' in page:
                    relevant_box = page.MediaBox
                else:
                    # fall back to ANSI A (US Letter) if neither CropBox nor MediaBox are defined
                    # unlikely, but possible
                    relevant_box = None

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

        return asdict(result)

    except BaseException as e:
        logger.error(e, exc_info=True)
        return None


def fill_font(key: str, value: Any, level: int, fonts: dict, font: PdfPageFontReport):
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

    except BaseException as e:
        # logger.error(e, exc_info=True)
        pass


def load_font(key: str, value: Any, level: int, fonts: dict, font: PdfPageFontReport):
    """ """

    fill_font(key, value, level, fonts, font)

    # print(level, " " * level, key, ":", type(value), font)

    if isinstance(value, Dictionary):
        for child_key, child_value in value.items():
            load_font(child_key, child_value, level+1, fonts, font)
