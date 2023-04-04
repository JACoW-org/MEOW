
import sys
import json
import argparse

from fitz import Document


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]


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

                extracted = doc.extract_font(xref)
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

    report = json.dumps(dict(
        page_count=doc.page_count,
        pages_report=pages_report,
        fonts_report=fonts_report
    ))

    sys.stdout.write(f"{report}\n")

    doc.close()
    del doc


def main():
    """ """

    parser = argparse.ArgumentParser(
        prog="meow",
        description="MEOW CLI - Command line interface",
    )

    parser.add_argument(
        'stdin',
        type=argparse.FileType('r'),
        default=sys.stdin,
    )

    args = parser.parse_args(['-'])

    if args.stdin.isatty():
        parser.print_help()
        return 0

    line = args.stdin.readline()

    if not line:
        parser.exit(0)

    req = json.loads(line)

    method = req.get('method', '')
    params = req.get('params', {})

    if method == 'report':
        doc_report(dotdict(**params))


if __name__ == "__main__":
    while 1:
        main()
