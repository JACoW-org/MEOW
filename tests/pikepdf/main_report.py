

from io import BytesIO
from pprint import pprint
from anyio import Path
from pikepdf import Pdf, Page, Annotation, Rectangle
from pikepdf.objects import Name, Dictionary, Array
from reportlab.pdfgen import canvas


async def main():
    # await annotation()
    # await linearize()
    await merge()


async def annotation():

    paper_pdf_path: Path = Path('var/run/41_pdf/WEZG1.pdf')

    with Pdf.open(str(paper_pdf_path)) as pdf_doc:

        print(str(paper_pdf_path))

        print(pdf_doc.pages[0])
        # print(pdf_doc.pages[0].Annots)


async def linearize():

    paper_pdf_path: Path = Path('var/run/41_tmp/WEZG1.pdf')

    jacow_pdf_path: Path = Path('var/run/18_tmp/WEZG1.pdf_jacow')

    print(str(paper_pdf_path))

    with Pdf.open(str(paper_pdf_path)) as pdf_doc:

        with pdf_doc.open_metadata() as meta:
            meta['dc:title'] = "Let's change the title"
            pprint(meta)

        first_page: Page = Page(pdf_doc.pages[0])

        annotation_dict = {
            "/Type": "/Annot",
            "/Subtype": "/Text",
            "/Rect": [100, 100, 125, 125],
            "/C": [0.97, 0.98, 0.31],  # yellow
            "/Contents": "Test comment",
            # "/P": page_ref,
            "/Name": "Help",
            "/T": "Joe Bloggs"
        }

        annotation = Annotation(Dictionary(annotation_dict))

        first_page.Annots = Array([annotation])

        # first_page.Annots = pdf_doc.make_indirect(Array([annotation]))

        # first_page.add_resource(resource, Name.Annot)

        pprint(first_page)

        # pdf_doc.flatten_annotations('all')

        pdf_doc.save(str(jacow_pdf_path),
                     linearize=True,
                     fix_metadata_version=True,
                     compress_streams=True)

        print(str(jacow_pdf_path))


def generate_watermark(msg: str, xy):
    x, y = xy
    buf = BytesIO()
    c = canvas.Canvas(buf, bottomup=0)
    c.setFontSize(32)
    c.setFillColorCMYK(0, 0, 0, 0, alpha=0.7)
    c.rect(204, 199, 157, 15, stroke=0, fill=1)
    c.setFillColorCMYK(0, 0, 0, 100, alpha=0.7)
    c.drawString(x, y, msg)
    c.save()
    buf.seek(0)
    return buf


async def merge():

    pdf_vol = Pdf.new()

    pdf_folder = Path('var/run/41_pdf/')

    async for pdf in pdf_folder.glob('*.pdf'):

        if str(pdf).endswith('41.pdf'):
            continue

        print(str(pdf))

        with Pdf.open(str(pdf)) as pdf_curr:

            for page in pdf_curr.pages:
                # print(page.get("/Annots"))
                del page.Annots

            txt = generate_watermark('Document text ', (0, 0))

            with Pdf.open(txt) as pdf_txt:
                print(pdf_txt.pages[0])
                Page(pdf_curr.pages[0]).add_overlay(
                    Page(pdf_txt.pages[0]),
                    Rectangle(0, 0, 500, 500))

            pdf_vol.pages.extend(pdf_curr.pages)

    pdf_name = Path('var/run/41_pdf/41.pdf')

    pdf_vol.remove_unreferenced_resources()

    def callback(count: int):
        print(count)

    pdf_vol.save(str(pdf_name),
                 linearize=True,
                 progress=callback,
                 fix_metadata_version=True)
