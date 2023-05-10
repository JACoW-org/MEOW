import io
import sys
import json
import pathlib
import argparse

from fitz import Document, Rect, Font
from fitz.utils import set_metadata, insert_link

from meow.services.local.papers_metadata.pdf_annotations import annot_page_footer, annot_page_header, annot_page_side


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
        except:
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

    doc_list = args.input  # a list of input PDFs
    doc = Document()  # output PDF

    for src_item in doc_list:  # process one input PDF

        src_list = src_item.split(",")
        password = src_list[1] if len(src_list) > 1 else None
        src = open_file(src_list[0], password, pdf=True)
        pages = ",".join(src_list[2:])  # get 'pages' specifications

        if pages:  # if anything there, retrieve a list of desired pages
            page_list = get_list(",".join(src_list[2:]), src.page_count + 1)
        else:  # take all pages
            page_list = range(1, src.page_count + 1)
        for i in page_list:
            # copy each source page
            doc.insert_pdf(src, from_page=i - 1, to_page=i - 1)

        src.close()
        del src

    doc.save(args.output, garbage=1, clean=1, deflate=1)

    doc.close()
    del doc


def doc_links(args) -> None:
    """ Add page links. """

    # print(args.input)
    # print(args.links)

    doc = Document(filename=args.input)

    # print("page_count", doc.page_count)
    # print("links_count", len(args.links))

    reversed_links = [l for l in args.links]
    reversed_links.reverse()

    for index, link in enumerate(reversed_links):
        page_index = (doc.page_count - index) - 1

        page = doc.load_page(page_index)

        # print(page_index, link, page.mediabox_size.x, page.mediabox_size.y)

        rect = Rect(0, 0, page.mediabox_size.x, page.mediabox_size.y)
        insert_link(page, {'kind': 2, 'from': rect, 'uri': f"{link}"})

    doc.save(filename=args.input, incremental=1, encryption=0)

    doc.close()
    del doc


def doc_text(args) -> None:

    doc = Document(filename=args.input)

    out = io.StringIO()

    for page in doc:  # iterate the document pages
        text = page.get_textpage().extractText()  # get plain text (is in UTF-8)
        out.write(text)  # write text of page

    txt = out.getvalue()

    sys.stdout.write(f"{txt}\n")

    doc.close()
    del doc


def doc_frame(args) -> None:

    doc = Document(filename=args.input)

    # logger.info(metadata)
    page_num = int(args.page)

    header = json.loads(args.header)
    footer = json.loads(args.footer)

    cc_logo = pathlib.Path('cc_by.png').read_bytes()

    for page in doc:

        if header:
            annot_page_header(page, header)

        if footer:
            annot_page_footer(page, page_num, footer)

        annot_page_side(
            page=page,
            page_number=page_num,
            cc_logo=cc_logo
        )

        page_num += 1

    doc.save(filename=args.input, incremental=1, encryption=0)

    doc.close()
    del doc


def doc_report(args) -> None:

    doc = Document(filename=args.input)

    pages_report = []
    fonts_report = []
    xref_list = []

    for page in doc:

        for font in page.get_fonts(True):

            xref = font[0]

            if xref not in xref_list:

                xref_list.append(xref)

                font_name, font_ext, font_type, buffer = doc.extract_font(xref)
                font_emb = not ((font_ext == "n/a" or not buffer) and font_type != "Type3")

                # print("{: >40} {: >5} {: >5} {: >5}".format(
                #     font_name, font_emb, font_ext, font_type
                # ))
                
                # print(buffer)

                # print("font_name", font_name, "font_emb", font_emb, "font_ext", font_ext, "font_type", font_type, len(buffer)) # font.name, font.flags, font.bbox, font.buffer

                fonts_report.append(dict(name=font_name, emb=font_emb,
                                         ext=font_ext, type=font_type))

        page_report = dict(sizes=dict(width=page.mediabox_size.x,
                                      height=page.mediabox_size.y))

        pages_report.append(page_report)

    fonts_report.sort(key=lambda x: x.get('name'))

    report = json.dumps(dict(
        page_count=doc.page_count,
        pages_report=pages_report,
        fonts_report=fonts_report
    ))

    sys.stdout.write(f"{report}\n")

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

    set_metadata(doc, meta)

    if args.output:
        doc.save(filename=args.output, garbage=1, clean=1, deflate=1)
    else:
        doc.save(filename=args.input, incremental=1, encryption=0)

    doc.close()
    del doc


def main():
    """ """

    parser = argparse.ArgumentParser(
        prog="meow",
        description="MEOW CLI - Command line interface",
    )

    subps = parser.add_subparsers(
        title="Subcommands", help="Enter 'command -h' for subcommand specific help"
    )

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
    ps_report.set_defaults(func=doc_report)

    # -------------------------------------------------------------------------
    # 'frame' command
    # -------------------------------------------------------------------------
    ps_frame = subps.add_parser(
        "frame",
        description="write PDF frame",
        epilog="specify input file",
    )
    ps_frame.add_argument("-input", required=True, help="input filename")
    ps_frame.add_argument("-header", required=True, help="header metadata")
    ps_frame.add_argument("-footer", required=True, help="header metadata")
    ps_frame.add_argument("-page", required=True, help="start page index")
    ps_frame.set_defaults(func=doc_frame)

    # -------------------------------------------------------------------------
    # 'metadata' command
    # -------------------------------------------------------------------------
    ps_metadata = subps.add_parser(
        "metadata",
        description="metadata PDF documents",
        epilog="specify each metadata field",
    )
    ps_metadata.add_argument("-author", help="author metadata field")
    ps_metadata.add_argument("-producer", help="producer metadata field")
    ps_metadata.add_argument("-creator", help="creator metadata field")
    ps_metadata.add_argument("-title", help="title metadata field")
    ps_metadata.add_argument("-format", help="format metadata field")
    ps_metadata.add_argument("-encryption", help="encryption metadata field")
    ps_metadata.add_argument(
        "-creationDate", help="creationDate metadata field")
    ps_metadata.add_argument("-modDate", help="modDate metadata field")
    ps_metadata.add_argument("-subject", help="subject metadata field")
    ps_metadata.add_argument("-keywords", help="keywords metadata field")
    ps_metadata.add_argument("-trapped", help="trapped metadata field")
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
    ps_links.set_defaults(func=doc_links)

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
