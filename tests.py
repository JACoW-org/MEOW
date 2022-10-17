import anyio

from tests.gen.async_gen import async_gen as main


if __name__ == '__main__':
    anyio.run(main)
