"""

Esecuzione parallela all'interno di un task group

"""

from anyio import run_process, create_task_group, run, CapacityLimiter
from typing import Any

import sys
import io
import pathlib
import hashlib

from anyio import run, to_process
from anyio import open_file, run

from pikepdf import open
from pikepdf.objects import Object  # type: ignore
from pikepdf.objects import Dictionary, String, Array, Stream

from jpsp.utils.http import download_stream
from jpsp.utils.serialization import json_encode

async def print_element(key: str, value: Any, level: int, fonts: dict, font: dict):
    """ """
   
    if level == 2 and key == '/BaseFont':
        font['name'] = str(value)
        fonts[str(value)] = font
        
    if level == 2 and key == '/Encoding':
        font['encoding'] = str(value)
    
    if level == 2 and key == '/Encoding':
        font['encoding'] = str(value)
    
    if level == 2 and key == '/Type':
        font['type'] = str(value)
        
    if level == 2 and key == '/Subtype':
        font['subtype'] = str(value)
        
    if level == 3 and key in ['/FontFile', '/FontFile2', '/FontFile3']:
        font['embedded'] = True    
     
    # print(level, " " * level, key, ":", type(value))

    if isinstance(value, int):
        print(level, " " * level, key, ":", value)
    if isinstance(value, String):
        print(level, " " * level, key, ":", value)
    elif isinstance(value, Dictionary):
        await print_dict(value, level+1, fonts, font)
    elif isinstance(value, Array):
        await print_array(key, value, level+1, fonts, font)
    elif isinstance(value, Stream):
        await print_stream(key, value, level+1, fonts, font)
    elif isinstance(value, Object):
        print(level, " " * level, key, ":", value)
        

async def print_array(key: str, array: Array, level: int, fonts: dict, font: dict):
    print(level, " " * level, key, 'array')
    # print(array.to_json())
    # for el in array.as_list():
    #     await print_element(key, el, level)

async def print_dict(dictionary: Dictionary, level: int, fonts: dict, font: dict):
    for key, value in dictionary.items():
        await print_element(key, value, level, fonts, font)

async def print_stream(key: str, stream: Stream, level: int, fonts: dict, font: dict):
    print(level, " " * level, key, 'stream')
    # print(stream.to_json())
    # print(stream.get_stream_buffer())
    
    

async def check_pdf(pdf_stream: io.BytesIO):

    # print("pdf_size", sys.getsizeof(pdf_stream))

    result: dict = dict()

    with open(pdf_stream) as p:

        result["page_count"] = len(p.pages)
        result["fonts"] = dict()

        for key, value in p.docinfo.items():
            if key in ['/Title', '/Author', '/CreationDate', '/Creator', '/ModDate', '/Producer']:
                await print_element(key, value, 0, result["fonts"], {})

        for page in p.pages:

            # print(page)
            
            if isinstance(page.obj, Array):
                for i in page.obj.keys():
                    await print_element("", i, 0, result["fonts"], {})
            else:
                for key, value in page.resources.items():
                    # print('0', key)
                    if key in ['/Font', '/FontFamily', '/FontName', '/Type', '/FontFile', '/FontFile2', '/FontFile3', '/Encoding', '/BaseFont', '/ToUnicode', '/DescendantFonts']:
                        print('0', key)
                        await print_element(key, value, 0, result["fonts"], {})
                        
            # print(result["fonts"])

            # print(res.to_json().decode())
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
                userunit = float(page.UserUnit)  # type: ignore

            # convert the box coordinates to float and multiply with the UserUnit
            relevant_box = [float(x)*userunit for x in relevant_box]  # type: ignore

            # obtain the dimensions of the box
            width = abs(relevant_box[2] - relevant_box[0])
            height = abs(relevant_box[3] - relevant_box[1])

            rotation = 0
            if '/Rotate' in page:
                rotation = page.Rotate

            # if the page is rotated clockwise or counter-clockwise, swap width and height
            # (pdf rotation modifies the coordinate system, so the box always refers to
            # the non-rotated page)
            if (rotation // 90) % 2 != 0:  # type: ignore
                width, height = height, width

            result['page_size'] = dict(
                width=width, height=height
            )

        # unembedded = fonts - embedded
        # print('Font List')
        # print(sorted(list(fonts)))
        # if unembedded:
        #     print('Unembedded Fonts')
        #     print(unembedded)

        p.close()

    pdf_stream.close()

    return result


async def main():

    SETTINGS = {
        "page_size_limit": "12x10",
        "page_count_limit": 300
    }

    PDF_FILE = {
        "url": "https://indico.jacow.org/event/44/contributions/349/attachments/227/751/AppleIII-Development_Tischer_FEL2022-THBI1.pdf",
        "_url": "https://vtechworks.lib.vt.edu/bitstream/handle/10919/73229/Base%2014%20Fonts.pdf?sequence=1&isAllowed=y",
        "name": "AppleIII-Development_Tischer_FEL2022-THBI1.pdf",
        "size": 4227793,
        "checksum": "1da86ed088b37886969d71876ac0ced6"
    }

    async def task(num: int, limiter: CapacityLimiter, file: dict):
        async with limiter:
            pdf_stream = await download_stream(file.get('url', None))

            # if not file.get("checksum", None) == str(hashlib.md5(pdf_stream.getbuffer()).hexdigest()):
            #     raise Exception("invalid checksum")
            
            # /home/fabio.meneghetti/Documents/RichiestaMutuo.pdf

            # result = await to_process.run_sync(check_pdf, pdf_stream)
            result = await check_pdf(pdf_stream)
            
            print('## page_count:', result['page_count'])
            print('## page_size:', result['page_size'])
            
            for key, font in result['fonts'].items():
                print('##', font['name'], font['encoding'], font['subtype'], font['embedded'])
            
            

    # await task()

    limiter = CapacityLimiter(20)
    async with create_task_group() as tg:
        for num in range(1):
            tg.start_soon(task, num, limiter, PDF_FILE)
            # await task(num, limiter, PDF_FILE)

    # result = await run_process('sleep 30')
    # print(result.stdout.decode())

    # check_pdf(pdf_stream)

    return None
