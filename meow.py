import argparse
import fitz
import sys

from fitz import Document

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

def doc_join(args):
    """Join pages from several PDF documents."""
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
            doc.insert_pdf(src, from_page=i - 1, to_page=i - 1)  # copy each source page
        src.close()

    doc.save(args.output, deflate=True)
    doc.close()
    
def main():
    print('main')
    parser = argparse.ArgumentParser(
        prog="meow",
        description="Basic MEOW Functions",
    )
    subps = parser.add_subparsers(
        title="Subcommands", help="Enter 'command -h' for subcommand specific help"
    )
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
    # start program
    # -------------------------------------------------------------------------
    args = parser.parse_args()  # create parameter arguments class
    if not hasattr(args, "func"):  # no function selected
        parser.print_help()  # so print top level help
    else:
        args.func(args)  # execute requested command
    
if __name__ == "__main__":
    main()
