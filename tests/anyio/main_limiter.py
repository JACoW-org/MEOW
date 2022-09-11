import anyio


async def use_resource(number, limiter):
    async with limiter:
        print('Task', number, 'is now working with the shared resource')
        await anyio.sleep(1)


async def main():
    limiter = anyio.CapacityLimiter(2)
    async with anyio.create_task_group() as tg:
        for i in range(10):
            tg.start_soon(use_resource, i, limiter)

anyio.run(main)
