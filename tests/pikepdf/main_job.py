"""

Esecuzione parallela all'interno di un task group

"""

import anyio
from pikepdf import open



async def main():
    
    with open('test.pdf') as my_pdf:
    for page in my_pdf.pages:
        page.Rotate = 180
    my_pdf.save('test-rotated.pdf')

    runtime = anyio.current_time() - start
    print(f'program executed in {runtime:.2f}s')

anyio.run(main)
