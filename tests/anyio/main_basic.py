"""

Esecuzione parallela all'interno di un task group

"""

import anyio


async def task(number):
    print('Task', number, 'is running')
    await anyio.sleep(5)
    print('Task', number, 'finished')


async def main():
    start = anyio.current_time()
    async with anyio.create_task_group() as tg:
        for i in range(5):
            tg.start_soon(task, i)

    runtime = anyio.current_time() - start
    print(f'program executed in {runtime:.2f}s')

anyio.run(main)
