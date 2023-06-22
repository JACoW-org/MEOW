
import io
import pathlib
import logging as lg
from anyio import Path, to_process

from meow.utils.hash import file_md5
from meow.utils.keywords import KEYWORDS
from meow.utils.process import run_cmd
from meow.utils.serialization import json_decode, json_encode

from fitz import Document
from fitz.utils import set_metadata


from nltk.stem.snowball import SnowballStemmer
from meow.services.local.papers_metadata.pdf_keywords import get_keywords_from_text, stem_keywords_as_tree
from meow.services.local.papers_metadata.pdf_annotations import annot_page_footer, annot_page_header, annot_page_side

logger = lg.getLogger(__name__)


def get_python_cmd():
    return str(Path("venv", "bin", "python3"))


async def is_to_download(file: Path, md5: str) -> bool:
    """ """

    if md5 == '' or not await file.exists():
        return True

    file_path = str(await file.absolute())

    md5_hex = await file_md5(file_path)

    # print(file_path, md5, md5_hex)

    # is_to_download = md5 == '' or already_exists == False or md5 != hl.md5(await file.read_bytes()).hexdigest()

    # if is_to_download == True:
    #     print(await file.absolute(), '-->', 'download')
    # else:
    #     print(await file.absolute(), '-->', 'skip')

    # return is_to_download

    return md5 != md5_hex


async def extract_event_pdf_files(event: dict) -> list:
    """ """

    event_files = []

    for contribution in event.get('contributions', []):
        latest_revision = contribution.get('latest_revision', None)

        revisions_files = latest_revision.get('files', []) \
            if latest_revision is not None \
            else []

        event_files.extend(revisions_files)

    return event_files


async def read_report(read_path: str, keywords: bool) -> dict | None:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'report', '-input',
           read_path, '-keywords', str(keywords)]

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return json_decode(res.stdout.decode()) if res and res.returncode == 0 else None

   
def _read_report_thread(input: str, keywords: bool):
    doc = Document(filename=input)

    pdf_value = io.StringIO()

    pages_report = []
    fonts_report = []
    xref_list = []

    stemmer = SnowballStemmer("english") if keywords else None
    stem_keywords = stem_keywords_as_tree(KEYWORDS, stemmer) if keywords and stemmer else None

    for page in doc:

        if keywords:
            # get plain text (is in UTF-8)
            pdf_value.write(page.get_textpage().extractText())

        for font in page.get_fonts(True):

            xref = font[0]

            if xref not in xref_list:

                xref_list.append(xref)

                font_name, font_ext, font_type, buffer = doc.extract_font(xref)
                font_emb = not ((font_ext == "n/a" or not buffer)
                                and font_type != "Type3")
                fonts_report.append(dict(name=font_name, emb=font_emb,
                                        ext=font_ext, type=font_type))

        page_report = dict(sizes=dict(width=page.mediabox_size.x,
                                    height=page.mediabox_size.y))

        pages_report.append(page_report)

    fonts_report.sort(key=lambda x: x.get('name'))

    keywords_list = get_keywords_from_text(str(pdf_value.getvalue()), stemmer, stem_keywords) \
        if stemmer and stem_keywords else []

    report = dict(
        page_count=doc.page_count,
        pages_report=pages_report,
        fonts_report=fonts_report,
        keywords=keywords_list
    )
    
    return report
    
async def read_report_anyio(read_path: str, keywords: bool) -> dict | None:
    return await to_process.run_sync(_read_report_thread, read_path, keywords)


async def pdf_to_text(read_path: str) -> str:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'text', '-input', read_path]

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.stdout.decode()

    return ''


async def draw_frame(read_path: str, write_path: str, page: int, pre_print: str | None, header: dict | None, footer: dict | None, metadata: dict | None) -> int:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'frame', '-input', read_path]

    cmd.append("-page")
    cmd.append(str(page))

    if pre_print:
        cmd.append("-preprint")
        cmd.append(pre_print)

    if header:
        cmd.append("-header")
        cmd.append(json_encode(header).decode('utf-8'))

    if footer:
        cmd.append("-footer")
        cmd.append(json_encode(footer).decode('utf-8'))

    if metadata:
        cmd.append("-metadata")
        cmd.append(json_encode(metadata).decode('utf-8'))
        
    cmd.append("-output")
    cmd.append(write_path)

    # logger.info(cmd)

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


def _draw_frame_thread_thread(input: str, output:str, page_number: int, pre_print: str | None, header: dict | None, footer: dict | None, metadata: dict | None):
    
    doc = Document(filename=input)

    if metadata:
        set_metadata(doc, metadata)

    cc_logo = pathlib.Path('cc_by.png').read_bytes()

    # print([args.input, page_number, pre_print])

    for page in doc:

        if header:
            annot_page_header(page, header)

        if footer:
            annot_page_footer(page, page_number, footer)

        annot_page_side(
            page=page,
            pre_print=pre_print,
            page_number=page_number,
            cc_logo=cc_logo
        )

        page_number += 1

    doc.save(filename=output, garbage=1, clean=1, deflate=1)

    doc.close()
    del doc

async def draw_frame_anyio(read_path: str, write_path: str, page: int, pre_print: str | None, header: dict | None, footer: dict | None, metadata: dict | None):
    return await to_process.run_sync(_draw_frame_thread_thread, read_path, write_path, page, pre_print, header, footer, metadata)

async def write_metadata(metadata: dict, read_path: str, write_path: str | None = None) -> int:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'metadata', '-input', read_path]

    if write_path is not None and write_path != '':
        cmd.append(f"-output")
        cmd.append(write_path)

    for key in metadata.keys():
        val = metadata.get(key, None)
        if val is not None and val != '':
            cmd.append(f"-{key}")
            cmd.append(val)

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def concat_pdf(write_path: str, files: list[str], metadata: dict | None) -> int:
    """ https://pymupdf.readthedocs.io/en/latest/tutorial.html#joining-and-splitting-pdf-documents """

    cmd = [get_python_cmd(), '-m', 'meow', 'join', '-o', write_path]
    
    

    res = await run_cmd(cmd + files)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.returncode

    return 1


async def brief_links(write_path: str, files: list[str]) -> int:
    """ https://github.com/pymupdf/PyMuPDF/issues/283 """

    cmd = [get_python_cmd(), '-m', 'meow', 'links', '-input', write_path]

    res = await run_cmd(cmd + files)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.returncode

    return 1
