"""

Esecuzione parallela all'interno di un task group

"""


import time

from anyio import run, to_process
from anyio import open_file, run

from jpsp.utils.http import download_stream

from pdfminer.high_level import extract_text, extract_text_to_fp

from io import StringIO
from pdfminer.layout import LAParams



from sklearn.feature_extraction.text import TfidfVectorizer



PDF = "/home/fabio.meneghetti/Projects/elettra/src/jpsp-ng/tests/pikepdf/AppleIII-Development_Tischer_FEL2022-THBI1.pdf"


async def main():
    
    start = time.time()
    
    output = StringIO()
    with open(PDF, 'rb') as fin:
        extract_text_to_fp(fin, output, laparams=LAParams(),
                            output_type='text', codec=None)
        
    print(output.getvalue())
    
    # create object
    tfidf = TfidfVectorizer()

    # get tf-df values
    result = tfidf.fit_transform([output.getvalue()])
    
    # get idf values
    print('\nidf values:')
    for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
        print(ele1, ':', ele2)
    
    end = time.time()
    
    print(end - start)
