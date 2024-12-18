import io
import sys
import json
import pathlib
import argparse
import pytz

import os
import gzip
import tarfile
import shutil
import multiprocessing as mp

from datetime import datetime, timezone

from fitz import Document, Page, Rect, Point, LINK_GOTO, LINK_URI
from fitz.utils import getColor, draw_rect, insert_textbox
from fitz.utils import set_metadata, insert_link, insert_text, new_page


from meow.services.local.papers_metadata.pdf_annots import (
    annot_page_footer, annot_page_header, annot_page_side
)
from meow.services.local.papers_metadata.pdf_annots import (
    annot_toc_footer, annot_toc_header
)

from anyio import run

from meow.services.local.papers_metadata.pdf_text import write_page_footer, write_page_header, write_page_side


def tz_convert(src_datetime, dest_timezone):

    dest_datetime = src_datetime.astimezone(pytz.timezone(dest_timezone))

    print(
        f"dest: {dest_timezone} - {dest_datetime.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")


def meow_tz(args) -> None:

    # "start_dt": {
    #     "date": "2024-05-19",
    #     "time": "15:00:00",
    #     "tz": "Europe/Zurich"
    # },

    # "start_dt": {
    #     "date": "2022-08-22",
    #     "time": "14:15:00",
    #     "tz": "UTC"
    # },

    # ./venv/bin/python3 -m meow tz
    # src: 2024-05-19 15:00:00 CEST+0200
    # dest: 2024-05-19 08:00:00 CDT-0500

    date_val = "2022-08-22"
    time_val = "14:15:00"
    tz_val = "UTC"

    src_timezone = pytz.timezone(tz_val)

    src_datetime = datetime.strptime(
        f"{date_val} {time_val}", '%Y-%m-%d %H:%M:%S')
    src_datetime = src_timezone.localize(src_datetime)

    print(f"src:  {tz_val} - {src_datetime.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

    # print(date_val, time_val)

    tz_convert(src_datetime, "US/Central")
    tz_convert(src_datetime, "Europe/Zurich")
    tz_convert(src_datetime, "Europe/Rome")
    tz_convert(src_datetime, "UTC")


def meow_auth(args) -> None:

    async def _run():
        # from meow.app.instances.application import app
        from meow.app.instances.databases import dbs
        from ulid import ulid as ULID

        if args.list:

            keys = await dbs.redis_client.keys(
                'meow:credential:*')

            for k in keys:

                key = k.decode('utf-8')

                auth = key.split(":")[2]

                res = await dbs.redis_client.hmget(
                    key, 'user', 'host', 'date')  # type: ignore

                # print(res)

                user = res[0].decode('utf-8')
                host = res[1].decode('utf-8')
                date = res[2].decode('utf-8')

                # OLD
                #print(f"{user}:{auth}@{host} ({date})")
                
                # URI
                print(f"[{date}] - user={user} host={host} auth={auth}")
                
                # CONF2038 indico.jacow.org XXXXXXXXXXXXXXXXXXXXXXXXXX
                #print(f"{user} {host} {auth}")

            # res = [{key:key} for key in keys]

            # print(res)

        elif args.login:

            date = datetime.now().isoformat()  # type: ignore

            [user, host] = args.login.split('@')

            auth = ULID()

            res = await dbs.redis_client.hset(
                f'meow:credential:{auth}', 'user', user)  # type: ignore
            res = await dbs.redis_client.hset(
                f'meow:credential:{auth}', 'host', host)  # type: ignore
            res = await dbs.redis_client.hset(
                f'meow:credential:{auth}', 'date', date)  # type: ignore
            
            # OLD
            #print(f"{user}:{auth}@{host} ({date})")
                
            # URI
            print(f"[{date}] - user={user} host={host} auth={auth}")

            # CONF2038 indico.jacow.org XXXXXXXXXXXXXXXXXXXXXXXXXX
            #print(f"{user}:{key}@{host} ({date})")

        elif args.logout:

            auth = str(args.logout)

            key = f'meow:credential:{auth}'

            res = await dbs.redis_client.delete(
                key)  # type: ignore

            print(res)

        elif args.check:

            auth = str(args.check)

            key = f'meow:credential:{auth}'

            res = await dbs.redis_client.hmget(
                key, 'user', 'host', 'date')  # type: ignore

            if res and len(res) == 3 and res[0] and res[1] and res[2]:

                user = res[0].decode('utf-8')
                host = res[1].decode('utf-8')
                date = res[2].decode('utf-8')
                
                # CONF2038 indico.jacow.org XXXXXXXXXXXXXXXXXXXXXXXXXX

                print(f"[{date}] - user={user} host={host} auth={auth}")

            else:

                print('invalid auth key')

        await dbs.redis_client.aclose()

    run(_run)


def open_file(filename, password, show=False, pdf=True):
    """Open and authenticate a document."""
    doc = Document(filename)
    if not doc.is_pdf and pdf is True:
        sys.exit("this command supports PDF files only")
    rc = -1
    if not doc.needs_pass:
        return doc
    if password:
        rc = doc.authenticate(password)
        if not rc:
            sys.exit("authentication unsuccessful")
        if show is True:
            print("authenticated as %s" % "owner" if rc > 2 else "user")
    else:
        sys.exit("'%s' requires a password" % doc.name)
    return doc


def get_list(rlist, limit, what="page"):
    """Transform a page / xref specification into a list of integers.

    Args
    ----
        rlist: (str) the specification
        limit: maximum number, i.e. number of pages, number of objects
        what: a string to be used in error messages
    Returns
    -------
        A list of integers representing the specification.
    """
    N = str(limit - 1)
    rlist = rlist.replace("N", N).replace(" ", "")
    rlist_arr = rlist.split(",")
    out_list = []
    for seq, item in enumerate(rlist_arr):
        n = seq + 1
        if item.isdecimal():  # a single integer
            i = int(item)
            if 1 <= i < limit:
                out_list.append(int(item))
            else:
                sys.exit("bad %s specification at item %i" % (what, n))
            continue
        try:  # this must be a range now, and all of the following must work:
            i1, i2 = item.split("-")  # will fail if not 2 items produced
            i1 = int(i1)  # will fail on non-integers
            i2 = int(i2)
        except BaseException:
            sys.exit("bad %s range specification at item %i" % (what, n))

        if not (1 <= i1 < limit and 1 <= i2 < limit):
            sys.exit("bad %s range specification at item %i" % (what, n))

        if i1 == i2:  # just in case: a range of equal numbers
            out_list.append(i1)
            continue

        if i1 < i2:  # first less than second
            out_list += list(range(i1, i2 + 1))
        else:  # first larger than second
            out_list += list(range(i1, i2 - 1, -1))

    return out_list


def doc_join(args) -> None:
    """ Join pages from several PDF documents. """

    doc = Document()  # output PDF

    # print(args.input)

    for src_item in args.input:  # process one input PDF

        # print(src_item)

        src_list = src_item.split(",")
        password = src_list[1] if len(src_list) > 1 else None
        src = open_file(src_list[0], password, pdf=True)
        pages = ",".join(src_list[2:])  # get 'pages' specifications

        if pages:  # if anything there, retrieve a list of desired pages
            page_list = get_list(",".join(src_list[2:]), src.page_count + 1)
        else:  # take all pages
            page_list = range(1, src.page_count + 1)

        # print(page_list)

        for i in page_list:
            # copy each source page
            doc.insert_pdf(src, from_page=i - 1, to_page=i - 1)

        src.close()
        del src

    if args.metadata:
        set_metadata(doc, json.loads(args.metadata))

    doc.save(args.output)

    doc.close()
    del doc


def doc_links(args) -> None:
    """ Add page links. """

    # print(args.input)
    # print(args.links)

    doc = Document(filename=args.input)

    # print("page_count", doc.page_count)
    # print("links_count", len(args.links))

    reversed_links = [link for link in args.links]
    reversed_links.reverse()

    for index, link in enumerate(reversed_links):
        page_index = (doc.page_count - index) - 1

        page = doc.load_page(page_index)

        # print(page_index, link, page.mediabox_size.x, page.mediabox_size.y)

        rect = Rect(0, 0, page.mediabox_size.x, page.mediabox_size.y)
        insert_link(page, {'kind': LINK_URI, 'from': rect, 'uri': f"{link}"})

    doc.save(args.output)

    doc.close()
    del doc


def doc_frame(args) -> None:

    doc = Document(filename=args.input)

    page_number = int(args.page)
    pre_print = args.preprint

    header = json.loads(args.header)
    footer = json.loads(args.footer)

    if args.metadata:
        set_metadata(doc, json.loads(args.metadata))

    cc_logo = pathlib.Path('cc_by.png').read_bytes()

    # print([args.input, page_number, pre_print])

    for page in doc:

        annot_page_header(
            page=page,
            data=header
        )

        annot_page_footer(
            page=page,
            page_number=page_number,
            data=footer
        )

        annot_page_side(
            page=page,
            pre_print=pre_print,
            page_number=page_number,
            cc_logo=cc_logo
        )

        page_number += 1

    doc.save(filename=args.output)

    doc.close()
    del doc


def doc_test(args) -> None:

    PAGE_WIDTH = 595
    PAGE_HEIGHT = 792

    TEXT_ALIGN_LEFT = 0

    PAGE_HORIZONTAL_MARGIN = 57
    PAGE_VERTICAL_MARGIN = 15
    LINE_SPACING = 3
    ANNOTATION_HEIGHT = 12
    SIDENOTE_LENGTH = 650
    TEXT_COLOR = getColor('GRAY10')
    TEXT_FILL = getColor('GRAY99')
    FONT_SIZE = 7
    # FONT_NAME = 'notos'
    FONT_NAME = 'helv'

    doc = Document()
    page = new_page(doc, width=PAGE_WIDTH, height=PAGE_HEIGHT)

    print(page.rect.width)

    rect_width = page.rect.width - 2 * PAGE_HORIZONTAL_MARGIN

    print(rect_width)

    # Rect(57.0, 15.0, 538.0, 25.0)

    rect = Rect(PAGE_HORIZONTAL_MARGIN,
                PAGE_VERTICAL_MARGIN,
                PAGE_HORIZONTAL_MARGIN + rect_width,
                PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT)

    print(rect)

    # text = "This is a preprint --- the final version is --- [published with IOP]"

    # font = Font('cjk')

    # page.insert_font(fontname='cjk', fontbuffer=font.buffer)

    data = dict()
    opt = dict()

    cc_logo = pathlib.Path('cc_by.png').read_bytes()

    draw_rect(page=page,
              rect=rect,
              color=TEXT_COLOR)

    insert_textbox(page=page,
                   rect=rect,
                   # rect=Rect(PAGE_HORIZONTAL_MARGIN,
                   #           PAGE_VERTICAL_MARGIN, PAGE_HORIZONTAL_MARGIN + rect_width,
                   #           PAGE_VERTICAL_MARGIN + ANNOTATION_HEIGHT),
                   align=TEXT_ALIGN_LEFT,
                   buffer='Seriesgmpl',
                   fontname=FONT_NAME,
                   fontsize=FONT_SIZE,
                   color=TEXT_COLOR,
                   )

    write_page_header(page, data, opt)

    write_page_footer(page, 1, data, opt)

    write_page_side(page, '', 1, cc_logo)

    # insert_textbox(page,
    #                rect=Rect(50,
    #                          50,
    #                          500,
    #                          500),
    #                buffer=text,
    #                fontname='helv',
    #                # encoding=0,
    #                fontsize=11)

    doc.save(filename=args.output)
    del doc


def doc_text(args) -> None:

    doc = Document(filename=args.input)

    out = io.StringIO()

    for page in doc:  # iterate the document pages
        text = page.get_textpage().extractText()  # get UTF-8 txt
        out.write(text)  # write text of page

    txt = out.getvalue()

    sys.stdout.write(f"{txt}\n")

    doc.close()
    del doc


def doc_report(args) -> None:

    from meow.utils.keywords import KEYWORDS
    from nltk.stem.snowball import SnowballStemmer
    from meow.services.local.papers_metadata.pdf_keywords import (
        get_keywords_from_text, stem_keywords_as_tree
    )

    doc = Document(filename=args.input)

    pdf_value = io.StringIO()

    pages_report = []
    fonts_report = []
    xref_list = []

    stemmer = SnowballStemmer("english") if args.keywords == 'True' else None
    stem_keywords = stem_keywords_as_tree(
        KEYWORDS, stemmer) if stemmer else None

    for page in doc:

        if args.keywords == 'True':
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

        page_width = page.rect.width
        page_height = page.rect.height

        # print(page.rect)
        # print(page.mediabox_size)

        page_report = dict(sizes=dict(width=page_width,
                                      height=page_height))

        pages_report.append(page_report)

    fonts_report.sort(key=lambda x: x.get('name'))

    pdf_text = str(pdf_value.getvalue()) if stemmer else ''
    keywords = get_keywords_from_text(pdf_text, stemmer, stem_keywords) \
        if stemmer and stem_keywords else []

    report = json.dumps(dict(
        page_count=doc.page_count,
        pages_report=pages_report,
        fonts_report=fonts_report,
        keywords=keywords
    ))

    sys.stdout.write(f"{report}\n")

    doc.close()
    del doc


def doc_toc_vol(args) -> None:

    toc_data: dict | None = None

    # print(args.config)

    with open(args.config) as f:
        contents = f.read()
        # print(contents)
        toc_data = json.loads(contents)

    if not toc_data:
        raise RuntimeError('Invalid config')

    PAGE_WIDTH = 595
    PAGE_HEIGHT = 792

    ITEMS_PER_PAGE = 46

    PAGE_HORIZONTAL_MARGIN = 57
    PAGE_VERTICAL_MARGIN = 57
    PAGE_VERTICAL_SPACE = 30
    ANNOTATION_HEIGHT = 10
    LINE_SPACING = 4
    LINE_LENGTH = 82

    RECT_WIDTH = PAGE_WIDTH - 2 * PAGE_HORIZONTAL_MARGIN

    event: dict = toc_data.get('event', None)
    pre_pdf: str = toc_data.get('pre_pdf', None)

    if not pre_pdf:
        start_page = 0
    else:
        pre_doc: Document = Document(filename=pre_pdf)
        start_page = int(pre_doc.page_count)
        pre_doc.close()
        del pre_doc

    items = [{}, {}] + toc_data.get('toc_items', [])
    settings = toc_data.get('toc_settings', {})

    # track_group_indent is added just as a reference, if it's left at 0, it's not really necessary
    track_group_indent = 0
    track_indent = track_group_indent + \
        (2 if settings.get('include_track_group') else 0)

    session_indent = 0
    contribution_indent: int = session_indent + \
        (2 if settings.get('include_sessions') else 0)

    # total_pages = math.ceil(len(items) / ITEMS_PER_PAGE)

    json_links: list = []

    doc: Document = Document()

    page: Page = new_page(doc, width=PAGE_WIDTH, height=PAGE_HEIGHT)

    annot_toc_header(
        page=page,
        data=event
    )

    annot_toc_footer(
        page=page,
        data=event,
        page_number=start_page + (page.number or 0) + 1,
    )

    toc_title = toc_data.get('toc_title', 'Table of Contents')

    toc_title_point = Point(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN +
                            PAGE_VERTICAL_SPACE + LINE_SPACING)

    insert_text(page,
                toc_title_point,
                f"{toc_title}",
                fontname="CoBo",
                fontsize=11)

    item_index = 0
    page_number = start_page + (page.number or 0)

    for i, item in enumerate(items):

        if i < 2:
            continue

        item_index = i % ITEMS_PER_PAGE

        if item_index == 0:
            page = new_page(doc, width=PAGE_WIDTH, height=PAGE_HEIGHT)

            page_number = start_page + (page.number or 0)

            annot_toc_header(
                page=page,
                data=event
            )

            annot_toc_footer(
                page=page,
                data=event,
                page_number=page_number + 1,
            )

        space = (item_index * (LINE_SPACING + ANNOTATION_HEIGHT)) + \
            (PAGE_VERTICAL_SPACE)

        def truncate_text(initial_text: str, text_indent: int) -> str:
            truncated_sign = ' [...]'
            truncated_text = ''

            for word in initial_text.split():
                if len(truncated_text) + len(word) < LINE_LENGTH - text_indent - len(truncated_sign):
                    truncated_text += ' ' + word
                else:
                    break

            if len(truncated_text) < len(initial_text):
                truncated_text += truncated_sign

            truncated_text = ' ' * text_indent + truncated_text

            return truncated_text

        if item.get('type') == 'contribution':

            contribution_text_point = Point(PAGE_HORIZONTAL_MARGIN,
                                            PAGE_VERTICAL_MARGIN + space)

            contribution_title = item.get(
                'code', '') + ' - ' + item.get('title', '')

            contribution_text = truncate_text(
                contribution_title, contribution_indent)

            contribution_text = f"{contribution_text:.<{LINE_LENGTH}}"

            insert_text(page, contribution_text_point,
                        contribution_text,
                        fontname="Cour",
                        fontsize=9)

        elif item.get('type') == 'session':
            session_text_point = Point(PAGE_HORIZONTAL_MARGIN,
                                       PAGE_VERTICAL_MARGIN + space)

            session_title = (' ' * session_indent) + \
                item.get('title', '').upper()

            session_text = truncate_text(
                session_title, session_indent)

            session_text = f"{session_text:.<{LINE_LENGTH}}"

            insert_text(page, session_text_point,
                        session_text,
                        fontname="CoBo",
                        fontsize=9)

        elif item.get('type') == 'track':
            track_text_point = Point(PAGE_HORIZONTAL_MARGIN,
                                     PAGE_VERTICAL_MARGIN + space)

            track_title = (' ' * track_indent) + item.get('title', '').upper()

            track_text = truncate_text(
                track_title, track_indent)

            insert_text(page, track_text_point,
                        track_text,
                        fontname="CoBo",
                        fontsize=9)

        elif item.get('type') == 'track_group':
            track_group_title_point = Point(PAGE_HORIZONTAL_MARGIN,
                                            PAGE_VERTICAL_MARGIN + space)

            track_group_title = (' ' * track_group_indent) + \
                item.get('title', '').upper()

            track_group_title = f"{track_group_title:.<{LINE_LENGTH}}"

            insert_text(page, track_group_title_point,
                        track_group_title,
                        fontname="CoBo",
                        fontsize=9)

        link_point = Point(PAGE_HORIZONTAL_MARGIN + RECT_WIDTH - 24,
                           PAGE_VERTICAL_MARGIN + space)

        insert_text(page,
                    link_point,
                    f"{item.get('page', 0):4d}",
                    fontname="CoBo",
                    fontsize=9)

        to_file = toc_data.get('vol_file', None)
        to_page = item.get('page', 0)

        link_rect = Rect(PAGE_HORIZONTAL_MARGIN, PAGE_VERTICAL_MARGIN
                         + space - 10, PAGE_HORIZONTAL_MARGIN +
                         RECT_WIDTH, PAGE_VERTICAL_MARGIN +
                         space + ANNOTATION_HEIGHT - 5)

        link_rect_json = dict(
            x0=link_rect.x0,
            y0=link_rect.y0,
            x1=link_rect.x1,
            y1=link_rect.y1,
        )

        json_link = {'kind': LINK_GOTO, 'from_rect': link_rect_json,
                     "from_page": page_number, "to_page": to_page,
                     "to_file": to_file, "to_point": (0, 0),
                     "code": item.get('title', '')}

        json_links.append(json_link)

    doc.save(args.output)

    meta = {
        "start_page": start_page,
        "total_pages": doc.page_count,
        "json_links": json_links,
    }

    with open(args.links, 'w') as f:
        f.write(json.dumps(meta))


def doc_toc_links(args) -> None:

    toc_data: dict | None = None

    # print(args.config)

    with open(args.links) as f:
        contents = f.read()
        # print(contents)
        toc_data = json.loads(contents)

    if not toc_data:
        exit(1)

    doc: Document = Document(filename=args.input)

    start_page = toc_data.get('start_page', 1) - 1
    total_pages = toc_data.get('total_pages', 0)
    json_links = toc_data.get('json_links', [])

    for json_link in json_links:

        # json_link = {'kind': LINK_GOTO, 'from_rect': link_rect_json,
        #              "from_page": page_number, "to_page": to_page,
        #              "to_file": to_file, "to_point": (0, 0),
        #              "code": item.get('title', '')}

        # print(json_link)

        link_kind = json_link.get('kind', 1)
        link_from = json_link.get('from_rect', {})

        from_page = json_link.get('from_page', 0)
        to_page = json_link.get('to_page', 0) + start_page + total_pages

        link_rect = Rect(link_from.get('x0'), link_from.get('y0'),
                         link_from.get('x1'), link_from.get('y1'))

        link: dict = {'kind': link_kind, 'from': link_rect, "page": to_page}

        page = doc.load_page(from_page)

        # print(page, link)

        insert_link(page, link, mark=True)

    doc.save(filename=args.output)
    doc.close()
    del doc


def doc_metadata(args) -> None:

    doc = Document(filename=args.input)

    meta = dict(
        author=args.author,
        producer=args.producer,
        creator=args.creator,
        title=args.title,
        format=args.format,
        encryption=args.encryption,
        creationDate=args.creationDate,
        modDate=args.modDate,
        subject=args.subject,
        keywords=args.keywords,
        trapped=args.trapped
    )

    doc.del_xml_metadata()

    set_metadata(doc, meta)

    doc.save(filename=args.output)

    doc.close()
    del doc


# https://www.driftinginrecursion.com/post/parallel_archiving/
# https://docs.python.org/3/library/tarfile.html#examples
def gzip_compress_file(p):
    print('gzip_compress_file', p, p + '.gz')
    with open(p, 'rb') as f:
        with gzip.open(p + '.gz', 'wb', compresslevel=1) as gz:
            shutil.copyfileobj(f, gz)  # type: ignore
    # os.remove(p)


def search_fs(p):
    file_list = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(p)) for f in fn]
    return file_list


def tar_dir(s):
    with tarfile.open(s + '.tar', 'w') as tar:
        for f in search_fs(s):
            tar.add(f, f[len(s):])


def compress_dir(args):

    folder = args.input

    files = search_fs(folder)
    procs = mp.cpu_count()
    with mp.Pool(procs) as pool:
        pool.map(gzip_compress_file, files)
        # r = list(tqdm.tqdm(pool.imap(gzip_compress_file, files),
        #                    total=len(files), desc='Compressing Files'))

        # r = list(tqdm.tqdm(
        #    pool.imap(gzip_compress_file, files),
        #
        #                   total=len(files), desc='Compressing Files'))

    print('Adding Compressed Files to TAR....')
    tar_dir(folder)

    # if rmbool == True:
    #     shutil.rmtree(dir)


def main():
    """ """

    parser = argparse.ArgumentParser(
        prog="meow",
        description="MEOW CLI - Command line interface",
    )

    subps = parser.add_subparsers(
        title="Subcommands",
        help="Enter 'command -h' for subcommand specific help"
    )

    # -------------------------------------------------------------------------
    # 'test' command
    # -------------------------------------------------------------------------
    ps_test = subps.add_parser(
        "test",
        description="get PDF test",
        epilog="specify output file",
    )
    ps_test.add_argument("-output", required=True, help="output filename")
    ps_test.set_defaults(func=doc_test)

    # -------------------------------------------------------------------------
    # 'report' command
    # -------------------------------------------------------------------------
    ps_text = subps.add_parser(
        "text",
        description="get PDF text",
        epilog="specify input file",
    )
    ps_text.add_argument("-input", required=True, help="input filename")
    ps_text.set_defaults(func=doc_text)

    # -------------------------------------------------------------------------
    # 'report' command
    # -------------------------------------------------------------------------
    ps_report = subps.add_parser(
        "report",
        description="get PDF report",
        epilog="specify input file",
    )
    ps_report.add_argument("-input", required=True, help="input filename")
    ps_report.add_argument("-keywords", required=False,
                           help="extract keywords")
    ps_report.set_defaults(func=doc_report)

    # -------------------------------------------------------------------------
    # 'toc_vol' command
    # -------------------------------------------------------------------------
    ps_toc_vol = subps.add_parser(
        "toc_vol",
        description="write TOC to pdf",
        epilog="specify output file, config and links",
    )
    ps_toc_vol.add_argument("-output", required=True, help="output filename")
    ps_toc_vol.add_argument("-config", required=False, help="toc config data")
    ps_toc_vol.add_argument("-links", required=False, help="toc metadata data")
    ps_toc_vol.set_defaults(func=doc_toc_vol)

    # -------------------------------------------------------------------------
    # 'toc_links' command
    # -------------------------------------------------------------------------
    ps_toc_links = subps.add_parser(
        "toc_links",
        description="write TOC links",
        epilog="specify input/output files and links",
    )
    ps_toc_links.add_argument("-input", required=True, help="input filename")
    ps_toc_links.add_argument("-output", required=True, help="output filename")
    ps_toc_links.add_argument("-links", required=True, help="toc links data")
    ps_toc_links.set_defaults(func=doc_toc_links)

    # -------------------------------------------------------------------------
    # 'frame' command
    # -------------------------------------------------------------------------
    ps_frame = subps.add_parser(
        "frame",
        description="write PDF frame",
        epilog="specify input file",
    )
    ps_frame.add_argument("-input", required=True, help="input filename")
    ps_frame.add_argument("-output", required=True, help="output filename")
    ps_frame.add_argument("-header", required=True, help="header metadata")
    ps_frame.add_argument("-footer", required=True, help="header metadata")
    ps_frame.add_argument("-page", required=True, help="start page index")
    ps_frame.add_argument("-preprint", required=False, help="preprint text")
    ps_frame.add_argument("-metadata", required=False, help="pdf metadata")

    ps_frame.set_defaults(func=doc_frame)

    # -------------------------------------------------------------------------
    # 'metadata' command
    # -------------------------------------------------------------------------
    ps_metadata = subps.add_parser(
        "metadata",
        description="metadata PDF documents",
        epilog="specify each metadata field",
    )
    ps_metadata.add_argument("-author", help="author field")
    ps_metadata.add_argument("-producer", help="producer field")
    ps_metadata.add_argument("-creator", help="creator field")
    ps_metadata.add_argument("-title", help="title field")
    ps_metadata.add_argument("-format", help="format field")
    ps_metadata.add_argument("-encryption", help="encryption field")
    ps_metadata.add_argument("-creationDate", help="creationDate field")
    ps_metadata.add_argument("-modDate", help="modDate field")
    ps_metadata.add_argument("-subject", help="subject field")
    ps_metadata.add_argument("-keywords", help="keywords field")
    ps_metadata.add_argument("-trapped", help="trapped field")
    ps_metadata.add_argument("-input", required=True, help="input filename")
    ps_metadata.add_argument("-output", help="output filename")
    ps_metadata.set_defaults(func=doc_metadata)

    # -------------------------------------------------------------------------
    # 'join' command
    # -------------------------------------------------------------------------
    ps_join = subps.add_parser(
        "join",
        description="join PDF documents",
        epilog="specify each input as 'filename[,password[,pages]]'",
    )
    ps_join.add_argument("input", nargs="*", help="input filenames")
    ps_join.add_argument("-output", required=True, help="output filename")
    ps_join.add_argument("-metadata", required=False, help="set metadata")
    ps_join.set_defaults(func=doc_join)

    # -------------------------------------------------------------------------
    # 'links' command
    # -------------------------------------------------------------------------
    ps_links = subps.add_parser(
        "links",
        description="insert page links",
        epilog="specify page links",
    )
    ps_links.add_argument("links", nargs="*", help="input links")
    ps_links.add_argument("-input", required=True, help="input filename")
    ps_links.add_argument("-output", required=True, help="output filename")
    ps_links.set_defaults(func=doc_links)

    # -------------------------------------------------------------------------
    # 'auth' command
    # -------------------------------------------------------------------------
    ps_auth = subps.add_parser(
        "auth",
        description="manage meow auth",
        epilog="manage meow auth",
    )
    ps_auth.add_argument("-list", required=False, help="list credentials",
                         action=argparse.BooleanOptionalAction)
    ps_auth.add_argument("-login", required=False, type=str,
                         help="login")
    ps_auth.add_argument("-logout", required=False, type=str,
                         help="logout")
    ps_auth.add_argument("-check", required=False, type=str,
                         help="check")
    ps_auth.set_defaults(func=meow_auth)

    # -------------------------------------------------------------------------
    # 'tz' command
    # -------------------------------------------------------------------------
    tz_auth = subps.add_parser(
        "tz",
        description="manage meow tz",
        epilog="manage meow tz",
    )
    tz_auth.set_defaults(func=meow_tz)

    # -------------------------------------------------------------------------
    # 'compress' command
    # -------------------------------------------------------------------------
    ps_compress = subps.add_parser(
        "compress",
        description="compress folder",
        epilog="specify folder to compress",
    )
    ps_compress.add_argument("-input", required=True, help="input dir")
    # ps_compress.add_argument("-output", required=True, help="output file")
    ps_compress.set_defaults(func=compress_dir)

    # -------------------------------------------------------------------------
    # start program
    # -------------------------------------------------------------------------
    args = parser.parse_args()  # create parameter arguments class
    if not hasattr(args, "func"):  # no function selected
        parser.print_help()  # so print top level help
    else:
        args.func(args)  # execute requested command


if __name__ == "__main__":
    main()
