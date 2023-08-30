
import io
import pathlib
import logging as lg
from anyio import Path, to_thread
from meow.services.local.papers_metadata.pdf_text import write_page_footer, write_page_header, write_page_side

from meow.utils.hash import file_md5
from meow.utils.keywords import KEYWORDS
from meow.utils.process import run_cmd
from meow.utils.serialization import json_decode, json_encode

from fitz import Document
from fitz.utils import set_metadata


from pikepdf import open

from nltk.stem.snowball import SnowballStemmer
from meow.services.local.papers_metadata.pdf_keywords import (
    get_keywords_from_text, stem_keywords_as_tree)
from meow.services.local.papers_metadata.pdf_annots import (
    annot_page_footer, annot_page_header, annot_page_side)


logger = lg.getLogger(__name__)


cc_logo = pathlib.Path('cc_by.png').read_bytes()


def get_python_cmd():
    return str(Path("venv", "bin", "python3"))


def get_pdftk_cmd():
    return str(Path("pdftk"))  # str(Path("bin", "pdftk"))


def get_mutool_cmd():
    return str(Path("mutool"))  # str(Path("bin", "mutool"))


def get_qpdf_cmd():
    return str(Path("qpdf"))  # str(Path("bin", "qpdf"))


def get_pdfunite_cmd():
    return str(Path("pdfunite"))  # str(Path("bin", "pdfunite"))


async def pdf_linearize_qpdf(in_path: str, out_path: str, docinfo: dict | None, metadata: dict | None):
    """ """

    with open(in_path) as pdf_doc:

        if docinfo:
            for key in docinfo:
                pdf_doc.docinfo[key] = docinfo[key]

        with pdf_doc.open_metadata(set_pikepdf_as_editor=False,
                                   update_docinfo=False) as pdf_meta:

            pdf_meta.clear()

            # print(pdf_meta)

            # if docinfo:
            #     pdf_meta.load_from_docinfo(
            #         docinfo, delete_missing=True, raise_failure=True)

            if metadata:
                for key in metadata:
                    pdf_meta[key] = metadata[key]

        pdf_doc.save(out_path, linearize=True, fix_metadata_version=True)

    return 0


async def pdf_metadata_qpdf(file_path: str, docinfo: dict | None, metadata: dict | None):
    """ """

    with open(file_path, allow_overwriting_input=True) as pdf_doc:

        # print(pdf_doc.docinfo)

        if docinfo:
            for key in docinfo:
                pdf_doc.docinfo[key] = docinfo[key]

        with pdf_doc.open_metadata(set_pikepdf_as_editor=False,
                                   update_docinfo=False) as pdf_meta:

            pdf_meta.clear()

            # print(pdf_meta)

            # if docinfo:
            #     pdf_meta.load_from_docinfo(
            #         docinfo, delete_missing=True, raise_failure=True)

            if metadata:
                for key in metadata:
                    pdf_meta[key] = metadata[key]

        pdf_doc.save(linearize=True, fix_metadata_version=True)


async def is_to_download(file: Path, md5: str) -> bool:
    """ """

    if md5 == '' or not await file.exists():
        return True

    file_path = str(await file.absolute())

    md5_hex = await file_md5(file_path)

    # print(file_path, md5, md5_hex)

    # is_to_download = md5 == '' or already_exists == False
    # or md5 != hl.md5(await file.read_bytes()).hexdigest()

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
            if latest_revision is not None else []

        event_files.extend(revisions_files)

    return event_files


async def read_report(read_path: str, keywords: bool) -> dict | None:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'report', '-input',
           read_path, '-keywords', str(keywords)]

    # print(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return json_decode(res.stdout.decode()) if res and (
        res.returncode == 0) else None


def _read_report_thread(input: str, keywords: bool):

    doc: Document | None = None

    try:

        doc = Document(filename=input)

        pdf_value = io.StringIO()

        pages_report = []
        fonts_report = []
        xref_list = []

        stemmer = SnowballStemmer(language="english") if keywords else None
        stem_keywords = stem_keywords_as_tree(
            KEYWORDS, stemmer) if keywords and stemmer else None

        for page in doc:

            if keywords:
                # get plain text (is in UTF-8)
                pdf_value.write(page.get_textpage().extractText())

            for font in page.get_fonts(True):

                xref = font[0]

                if xref not in xref_list:

                    xref_list.append(xref)

                    font_name, font_ext, font_type, buffer = doc.extract_font(
                        xref)
                    font_emb = not ((font_ext == "n/a" or not buffer)
                                    and font_type != "Type3")
                    fonts_report.append(dict(name=font_name, emb=font_emb,
                                             ext=font_ext, type=font_type))

            page_width = page.rect.width
            page_height = page.rect.height

            page_report = dict(sizes=dict(width=page_width,
                                          height=page_height))

            pages_report.append(page_report)

        fonts_report.sort(key=lambda x: x.get('name'))

        keywords_list = get_keywords_from_text(str(pdf_value.getvalue()),
                                               stemmer, stem_keywords) \
            if stemmer and stem_keywords else []

        report = dict(
            page_count=doc.page_count,
            pages_report=pages_report,
            fonts_report=fonts_report,
            keywords=keywords_list
        )

        return report

    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if doc is not None:
            doc.close()
            del doc


async def read_report_anyio(read_path: str, keywords: bool) -> dict | None:
    return await to_thread.run_sync(_read_report_thread, read_path, keywords)


async def pdf_to_text(read_path: str) -> str:
    """ """

    cmd = [get_python_cmd(), '-m', 'meow', 'text', '-input', read_path]

    # print(" ".join(cmd))

    res = await run_cmd(cmd)

    if res is not None and res.returncode == 0:

        # print(res.returncode)
        # print(res.stdout.decode())
        # print(res.stderr.decode())

        return res.stdout.decode()

    return ''


async def draw_frame(read_path: str, write_path: str, page: int,
                     pre_print: str | None, header: dict | None,
                     footer: dict | None, metadata: dict | None) -> int:
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

    # logger.info(" ".join(cmd))

    # print(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def draw_frame_anyio(input: str, output: str, page: int,
                           pre_print: str | None, header: dict | None,
                           footer: dict | None, metadata: dict | None,
                           xml_metadata: str | None, annotations: bool = True):
    return await to_thread.run_sync(_draw_frame_anyio, input, output,
                                    page, pre_print, header, footer, metadata,
                                    xml_metadata, annotations)


def _draw_frame_anyio(input: str, output: str, page_number: int,
                      pre_print: str | None, header: dict | None,
                      footer: dict | None, metadata: dict | None,
                      xml_metadata: str | None, annotations: bool = True):

    doc: Document | None = None

    try:

        doc = Document(filename=input)

        # scrub(doc,
        #       attached_files=False,
        #       clean_pages=False,
        #       embedded_files=False,
        #       hidden_text=True,
        #       javascript=True,
        #       metadata=True,
        #       redactions=False,
        #       redact_images=0,
        #       remove_links=False,
        #       reset_fields=False,
        #       reset_responses=True,
        #       thumbnails=False,
        #       xml_metadata=True)

        # set_page_labels(doc, [])

        doc.del_xml_metadata()

        if xml_metadata:
            doc.set_xml_metadata(xml_metadata)

        if metadata:
            set_metadata(doc, metadata)

        # logger.debug([input, output, page_number, pre_print])

        for page in doc:

            if header:
                annot_page_header(page, header) if annotations \
                    else write_page_header(page, header)

            if footer:
                annot_page_footer(page, page_number, footer) if annotations \
                    else write_page_footer(page, page_number, footer)

            annot_page_side(
                page=page,
                pre_print=pre_print,
                page_number=page_number,
                cc_logo=cc_logo
            ) if annotations \
                else write_page_side(
                page=page,
                pre_print=pre_print,
                page_number=page_number,
                cc_logo=cc_logo
            )

            page_number += 1

        # doc.save(filename=output, garbage=1, clean=1, deflate=1)
        doc.save(filename=output, garbage=1, clean=1, deflate=1)

    except BaseException as be:
        logger.error(be, exc_info=True)
        raise be
    finally:
        if doc is not None:
            doc.close()
            del doc


async def write_metadata(read_path: str, write_path: str, metadata: dict) -> int:
    """ """

    cmd = [get_python_cmd(), '-m',
           'meow', 'metadata', '-input',
           read_path, "-output", write_path]

    for key in metadata.keys():
        val = metadata.get(key, None)
        if val is not None and val != '':
            cmd.append(f"-{key}")
            cmd.append(val)

    # print(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_separate(input: str, output: str, first: int, last: int) -> int:
    # cmd = ['pdfseparate', '-f', str(first), '-l', str(last), input, output]

    # pdftk full-pdf.pdf cat 12-15 output outfile_p12-15.pdf

    cmd = [get_pdftk_cmd(), input, 'cat', f'{first}-{last}', 'output', output]

    # print(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_unite(write_path: str, files: list[str], first: bool) -> int:
    return await pdf_unite_pdftk(write_path, files, first)


async def pdf_unite_poppler(write_path: str, files: list[str], first: bool) -> int:

    cmd = [get_pdfunite_cmd()] + files + [write_path]

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     logger.info(res.returncode)
    #     logger.info(res.stdout.decode())
    #     logger.info(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_unite_pdftk(write_path: str, files: list[str], first: bool) -> int:

    if first is True:

        import string
        ascii = list(string.ascii_uppercase)

        labeled_files = []
        labeled_pages = []

        for index, file in enumerate(files):
            labeled_files.append(
                "".join([ascii[int(char)] for char in "{:06d}".format(index)])
                + "=" + file
            )
            labeled_pages.append(
                "".join([ascii[int(char)] for char in "{:06d}".format(index)])
                + "1"
            )

        cmd = [get_pdftk_cmd()] + labeled_files + ['cat'] + \
            labeled_pages + ['output'] + [write_path]

    else:

        cmd = [get_pdftk_cmd()] + files + ['cat'] + ['output'] + [write_path]

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_unite_qpdf(write_path: str, files: list[str], first: bool) -> int:

    # qpdf --linearize --remove-page-labels --empty --pages var/run/18_tmp/MOA03.pdf 1-1
    # var/run/18_tmp/MOA08.pdf 1-1 -- out.pdf

    # --linearize : ottimizza il pdf per la visualizzazione web
    # --remove-page-labels: serve per le pagine logiche

    items: list[str] = []

    for f in files:
        items.append(f)
        if first:
            items.append('1-1')

    cmd = [get_qpdf_cmd(), '--empty', '--pages'] + items + ['--', write_path]

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_unite_mutool(write_path: str, files: list[str], first: bool) -> int:

    # mutool merge -o out.pdf -O compress=yes ../../src/meow/var/run/18_tmp/
    #   18_proceedings_toc.pdf 1-N ../../src/meow/var/run/18_tmp/FRAI1.pdf 1-N
    #   ../../src/meow/var/run/18_tmp/FRAI2.pdf 1-N

    items: list[str] = []

    for f in files:
        items.append(f)
        items.append('1-1' if first else '1-N')

    # garbage[=compact|deduplicate],compress=yes,linearize=yes,sanitize=yes
    # '-O', 'garbage=yes,compress=yes,linearize=yes,sanitize=yes'
    cmd = [get_mutool_cmd(), 'merge', '-o', write_path] + items

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_clean(read_path: str, write_path: str) -> int:
    return await pdf_clean_qpdf(read_path, write_path)


async def pdf_clean_qpdf(read_path: str, write_path: str) -> int:

    # qpdf --linearize --remove-page-labels in.pdf -- out.pdf

    # --linearize : ottimizza il pdf per la visualizzazione web
    # --remove-page-labels: serve per le pagine logiche
    # --flatten-annotations: Push page annotations into the content streams

    cmd = [get_qpdf_cmd(),
           '--linearize',
           '--remove-page-labels',
           # '--remove-unreferenced-resources=yes',
           # '--flatten-annotations=all',
           read_path, '--', write_path]

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def pdf_clean_mutool(read_path: str, write_path: str) -> int:

    # ./bin/mutool clean -l var/run/18_tmp/18_proceedings_volume_clean.pdf
    #   var/run/18_tmp/18_proceedings_volume_mupdf.pdf 1-N

    # -l : ottimizza il pdf per la visualizzazione web
    # 1-N: serve per le pagine logiche

    cmd = [get_mutool_cmd(), 'clean', '-l', read_path, write_path, '1-N']

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def concat_pdf(write_path: str, files: list[str]) -> int:
    """ https://pymupdf.readthedocs.io/en/latest/tutorial.html
    #joining-and-splitting-pdf-documents """

    cmd = [get_python_cmd(), '-m', 'meow', 'join', '-o', write_path] + files

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def brief_links(read_path: str, write_path: str, files: list[str]) -> int:
    """ https://github.com/pymupdf/PyMuPDF/issues/283 """

    cmd = [get_python_cmd(), '-m', 'meow', 'links',
           '-input', read_path, '-output', write_path] + files

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def vol_toc_pdf(write_path: str, links_path: str, conf_path: str) -> int:

    cmd = [get_python_cmd(), '-m', 'meow', 'toc_vol']

    cmd.append("-c")
    cmd.append(conf_path)

    cmd.append("-o")
    cmd.append(write_path)

    cmd.append("-l")
    cmd.append(links_path)

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1


async def vol_toc_links(read_path: str, write_path: str, links_path: str) -> int:

    cmd = [get_python_cmd(), '-m', 'meow', 'toc_links']

    cmd.append("-i")
    cmd.append(read_path)

    cmd.append("-o")
    cmd.append(write_path)

    cmd.append("-l")
    cmd.append(links_path)

    logger.info(" ".join(cmd))

    res = await run_cmd(cmd)

    # if res:
    #     print(res.returncode)
    #     print(res.stdout.decode())
    #     print(res.stderr.decode())

    return 0 if res and res.returncode == 0 else 1
