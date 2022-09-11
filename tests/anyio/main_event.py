import anyio


async def task(event, number):
    print('Task', number, 'is waiting')
    await event.wait()
    print('Task', number, 'finished')


async def main():
    event = anyio.Event()
    async with anyio.create_task_group() as tg:
        for i in range(3):
            tg.start_soon(task, event, i)
        await anyio.sleep(1)
        # we wake up the tasks
        event.set()


anyio.run(main)
