"""

Esecuzione parallela all'interno di un task group

"""

from typing import Any
import anyio
import io
from pikepdf import open

from meow.utils.http import download_stream
from meow.utils.serialization import json_decode



async def main():
    
    event_stream: io.BytesIO = await download_stream('https://indico.jacow.org/export/event/44.json?detail=contributions')
    
    event_json: str = event_stream.read().decode('utf-8')
    
    response: Any = json_decode(event_json)
    
    event: dict = response['results'][0]
    
    contributions: list[dict] = event.get('contributions', [])
    
    def sort_func(e:dict):
        return int(e.get('id', '0'))
    
    contributions.sort(key=sort_func)
    
    for contribution in contributions:
        print(contribution.get('id'), contribution.get('code'), contribution.get('title'))
    
    # with open('test.pdf') as my_pdf:    


