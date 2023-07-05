
from ulid import ulid as ULID
import orjson
import anyio
import random

from anyio.abc import SocketAttribute


async def send_to(file_socket: str):
    async with await anyio.connect_unix(file_socket) as client:
        print('Connected to', client.extra(SocketAttribute.remote_address))

        req = dict(
            id=str(ULID()),
            header='request',
            body=random.random()
        )

        print(req)

        await client.send(orjson.dumps(req))

        res = orjson.loads(
            (await client.receive(4096)).decode()
        )

        print(res)


async def main():
    await send_to('/tmp/queue1')
    await send_to('/tmp/queue2')


anyio.run(main)
