
import asyncio


async def my_gen(u: int = 10):
    """Yield powers of 2."""

    i = 0
    while i < u:
        yield 2 ** i
        i += 1
        await asyncio.sleep(0.1)


async def async_gen():

    [print('x:', x) async for x in my_gen()]

    # This does *not* introduce concurrent execution
    # It is meant to show syntax only
    g = [i async for i in my_gen()]
    print(g)

    f = [j async for j in my_gen() if not (j // 3 % 5)]
    print(f)
