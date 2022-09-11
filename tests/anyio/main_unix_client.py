import anyio
from anyio.abc import SocketAttribute


async def main():
    async with await anyio.connect_unix('/tmp/mysock') as client:
        print('Connected to', client.extra(SocketAttribute.remote_address))
        await client.send(b'Client\n')
        response = await client.receive(1024)
        print(response)


anyio.run(main)
