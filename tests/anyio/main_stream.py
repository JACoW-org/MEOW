import anyio
from anyio import create_task_group, create_memory_object_stream, run


async def process_items(name, receive_stream):
    print(f'worker {name}...')
    async with receive_stream:
        async for item in receive_stream:
            print(f'received {name}', item)
            await anyio.sleep(1)


async def main():
    send_stream, receive_stream = create_memory_object_stream()
    async with create_task_group() as tg:
        tg.start_soon(process_items, '1', receive_stream.clone())
        tg.start_soon(process_items, '2', receive_stream.clone())
        with send_stream:
            for num in range(10):
                print(f'send {num}')
                send_stream.send_nowait(f'number {num}')

run(main)
