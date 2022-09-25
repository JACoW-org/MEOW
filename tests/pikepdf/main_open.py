"""

Esecuzione parallela all'interno di un task group

"""

from typing import Any
import anyio
import pathlib

from pikepdf import open
from pikepdf.objects import Dictionary

from jpsp.utils.http import download_file
from jpsp.utils.serialization import json_encode


PDF_FILE = "AppleIII-Development_Tischer_FEL2022-THBI1.pdf"
PDF_URL = f"https://indico.jacow.org/event/44/contributions/349/attachments/227/751/{PDF_FILE}"


fontkeys = set(['/FontFile', '/FontFile2', '/FontFile3'])


def font(obj: Dictionary, fnt, emb):
    
        
    for k in obj.keys():
        curr: Any = obj.get(k)
        
        print(k, type(curr))
        

def walk(obj: Dictionary, fnt, emb):
    
    print(type(obj))
     
    for k in obj.keys():
        
        curr: Any = obj.get(k)
        
        print(k, type(curr))
        
        if (k == "/Font"):
            
            font(curr, fnt, emb)
        
        
        #walk(, fnt, emb)
    
    # base_font = obj.get('/BaseFont')
    # if base_font is not None:
    #     fnt.add(base_font)
    #     
    # font_name = obj.get('/FontName')
    # if font_name is not None:
    #     emb.add(base_font)

    # for k in obj.keys():
    #      walk(obj.get(k), fnt, emb)

    return fnt, emb


async def main():
    
    base_path = pathlib.Path(__file__).parent
    pdf_path = base_path.joinpath(PDF_FILE)
    
    # await download_file(PDF_URL, pdf_path)
    
    with open(pdf_path) as my_pdf:
        
        print(my_pdf.filename)
        print(len(my_pdf.pages))
        
        print(my_pdf)
        
        docinfo = my_pdf.docinfo
        for key, value in docinfo.items():
            print(key, ":", value)
            
        fonts = set()
        embedded = set()
        
        for page in my_pdf.pages:
        
           
            #print(page)
            
            res: Dictionary = page.resources
            
            print(res.to_json())
            
            f, e = walk(res, fonts, embedded)
            
            fonts = fonts.union(f)
            embedded = embedded.union(e)
            
            # print(page.obj)
            
            
            if '/CropBox' in page:
                # use CropBox if defined since that's what the PDF viewer would usually display
                relevant_box = page.CropBox
            elif '/MediaBox' in page:
                relevant_box = page.MediaBox
            else:
                # fall back to ANSI A (US Letter) if neither CropBox nor MediaBox are defined
                # unlikely, but possible
                relevant_box = None

            # actually there could also be a viewer preference ViewArea or ViewClip in
            # pdf.Root.ViewerPreferences defining which box to use, but most PDF readers 
            # disregard this option anyway

            # check whether the page defines a UserUnit
            userunit = 1
            if '/UserUnit' in page:
                userunit = float(page.UserUnit)

            # convert the box coordinates to float and multiply with the UserUnit
            relevant_box = [float(x)*userunit for x in relevant_box]

            # obtain the dimensions of the box
            width  = abs(relevant_box[2] - relevant_box[0])
            height = abs(relevant_box[3] - relevant_box[1])

            rotation = 0
            if '/Rotate' in page:
                rotation = page.Rotate

            # if the page is rotated clockwise or counter-clockwise, swap width and height
            # (pdf rotation modifies the coordinate system, so the box always refers to 
            # the non-rotated page)
            if (rotation // 90) % 2 != 0:
                width, height = height, width
                
            print(width, height)


        unembedded = fonts - embedded
        print ('Font List')
        print(sorted(list(fonts)))
        if unembedded:
            print('Unembedded Fonts')
            print(unembedded)

anyio.run(main)
