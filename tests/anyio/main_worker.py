import anyio
import ujson
import random

from anyio import create_unix_listener, run
from anyio.abc import SocketStream
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream, WouldBlock


WORKERS_NUM: int = 2
    

async def computation(name: str, req: dict)-> dict:
    
    print(f"[{name}] - begin")
    
    for i in range(10):
        print(f"[{name}] - computation {i}")
        await anyio.sleep(0.5)
    
    print(f"[{name}] - end")
    
    return dict(
        id=req.get('id'),
        header='response',
        data=random.random()
    )


async def worker(name: str, receiver: MemoryObjectReceiveStream) -> bytes | None:
    print(f'worker {name} waiting...')
    
    async with receiver:
        async for req in receiver:
                
            print(f'worker {name} got value {req}')

            res = ujson.dumps(
                await computation(
                    name,
                    ujson.loads(req.decode())
                )
            ).encode()
            
            print(f'worker {name} ends')
              

async def unix_server(sender: MemoryObjectSendStream, file_socket: str) -> None:
   
    async with sender:
                           
        async def handle_client(client: SocketStream) -> None:
            print('handle_client...')                   
            async with client:
                req = await client.receive(4096)
                
                try:
                    sender.send_nowait(req)
                    await client.send(req)
                except WouldBlock as e:
                    await client.send(
                        ujson.dumps(
                            dict(err='Exhausted')
                        ).encode()
                    )
                except BaseException as e:
                    print(e)
                    await client.send(
                        ujson.dumps(
                            dict(err='Error')
                        ).encode()
                    )
        
        listener = await create_unix_listener(file_socket)
        print(f'server {file_socket} waiting...')
        await listener.serve(handle_client)


async def start_server(sender):
    print('start server...')
    async with anyio.create_task_group() as tg:
        async with sender:
            # unix_server
            tg.start_soon(unix_server, sender.clone(), '/tmp/queue1')
            tg.start_soon(unix_server, sender.clone(), '/tmp/queue2')


async def start_workers(receiver):
    print('start workers...')
    async with anyio.create_task_group() as tg:
        async with receiver:
            # workers
            for i in range(WORKERS_NUM):
                tg.start_soon(worker, i, receiver.clone())


async def main() -> None:

    sender, receiver = anyio.create_memory_object_stream(4)
    
    async with anyio.create_task_group() as tg:
        # server
        tg.start_soon(start_server, sender)
        # workers
        tg.start_soon(start_workers, receiver)


run(main)
