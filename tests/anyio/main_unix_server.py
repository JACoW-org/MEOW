from anyio import create_unix_listener, run


async def handle(client):
    async with client:
        name = await client.receive(1024)
        await client.send(b'Hello, %s\n' % name)


async def main():
    listener = await create_unix_listener('/tmp/mysock')
    await listener.serve(handle)


run(main)
