
import logging as lg

from io import open
from fitz import Document

from anyio import create_task_group, CapacityLimiter
from anyio import Path, to_process, to_thread, sleep
from anyio import create_memory_object_stream, ClosedResourceError

from anyio.streams.memory import MemoryObjectSendStream
from meow.services.local.event.event_pdf_utils import extract_event_pdf_files, is_to_download


from meow.utils.http import download_file

logger = lg.getLogger(__name__)


async def event_pdf_check(event: dict, cookies: dict, settings: dict):
    """ """

    # logger.debug(f'event_pdf_check - count: {len(contributions)} - cookies: {cookies}')

    event_id = event.get('id', 'event')

    pdf_cache_dir: Path = Path('var', 'run', f"{event_id}_pdf")
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)
    
    files = await extract_event_pdf_files(event)

    total_files: int = len(files)
    checked_files: int = 0

    # logger.debug(f'event_pdf_check - files: {len(files)}')

    send_stream, receive_stream = create_memory_object_stream()

    capacity_limiter = CapacityLimiter(4)

    async with create_task_group() as tg:
        async with send_stream:
            for current_index, current_file in enumerate(files):
                tg.start_soon(pdf_check_task, capacity_limiter, total_files, current_index,
                              current_file, cookies, pdf_cache_dir, send_stream.clone())

        try:
            async with receive_stream:
                async for report in receive_stream:
                    checked_files = checked_files + 1

                    # print('receive_reports_stream::report-->',
                    #       checked_files, total_files, report)

                    yield dict(
                        type='progress',
                        value=report
                    )

                    if checked_files >= total_files:
                        receive_stream.close()

                        yield dict(
                            type='final',
                            value=None
                        )

        except ClosedResourceError:
            pass



async def pdf_check_task(capacity_limiter: CapacityLimiter, total_files: int, current_index: int, current_file: dict,
                         cookies: dict, pdf_cache_dir: Path, res: MemoryObjectSendStream):
    """ """

    async with capacity_limiter:
        report = await internal_pdf_check_task(current_file, cookies, pdf_cache_dir)

        await res.send({
            "index": current_index,
            "total": total_files,
            "file": current_file,
            "report": report
        })


async def internal_pdf_check_task(current_file: dict, cookies: dict, pdf_cache_dir: Path):
    """ """

    pdf_md5 = current_file.get('md5sum', '')
    pdf_name = current_file.get('filename', '')
    http_sess = cookies.get('indico_session_http', '')
    pdf_url = current_file.get('external_download_url', '')

    pdf_file = Path(pdf_cache_dir, pdf_name)

    logger.debug(f"{pdf_md5} {pdf_name}")

    if await is_to_download(pdf_file, pdf_md5):
        cookies = dict(indico_session_http=http_sess)
        await download_file(url=pdf_url, file=pdf_file, cookies=cookies)

    # print(l.total_tokens)

    # IN PROCESS
    # return event_pdf_report(str(await pdf_file.absolute()))

    # EXTERNAL THREAD
    # return await to_thread.run_sync(event_pdf_report, str(await pdf_file.absolute()))

    # EXTERNAL PROCESS
    return await to_process.run_sync(event_pdf_report, str(await pdf_file.absolute()))


def event_pdf_report(path: str):
    """ """

    report = dict()

    # logger.info(f"event_pdf_report >>> {path}")

    with open(path, 'rb') as fh:
        try:
            pdf = Document(stream=fh.read(), filetype='pdf')
            report = extract_pdf_report(pdf)
            pdf.close()
        except Exception as e:
            logger.error(e, exc_info=True)

    # logger.info(f"event_pdf_report >>> {report}")

    return report


def extract_pdf_report(pdf: Document):

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
