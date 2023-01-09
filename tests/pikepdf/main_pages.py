"""

Esecuzione parallela all'interno di un task group

"""


import time

from anyio import run, to_process
from anyio import open_file, run

from jpsp.utils.http import download_stream

from io import StringIO

from sklearn.feature_extraction.text import TfidfVectorizer

from anyio import Path


PDF = "/home/fabio.meneghetti/Projects/elettra/src/jpsp-ng/tests/pikepdf/AppleIII-Development_Tischer_FEL2022-THBI1.pdf"


# def _pdf_to_txt() -> str:
#
#     from pdfminer.high_level import extract_text_to_fp
#     from pdfminer.layout import LAParams
#
#     out = StringIO()
#
#     with open(PDF, 'rb') as fin:
#          extract_text_to_fp(fin, out, laparams=LAParams(),
#                              output_type='text', codec=None)
#
#     return out.getvalue()


def pdf_to_txt(stream: bytes) -> str:

    from fitz import Document

    out = StringIO()

    doc = Document(stream=stream, filetype='pdf')

    for page in doc:  # iterate the document pages
        text = page.get_textpage().extractText()  # get plain text (is in UTF-8)
        out.write(text)  # write text of page

    return out.getvalue()


async def main():

    start = time.time()

    pdf = await Path(PDF).read_bytes()

    # print(time.time() - start)

    txt = pdf_to_txt(pdf)

    # print(txt)

    print(time.time() - start)

    # # create object
    # tfidf = TfidfVectorizer()
    #
    # # get tf-df values
    # result = tfidf.fit_transform([out.getvalue()])
    #
    # # get idf values
    # print('\nidf values:')
    # for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
    #     print(ele1, ':', ele2)
    #
    # print(time.time() - start)
