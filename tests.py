import anyio

from tests.ab.load import async_load as main


if __name__ == '__main__':
    anyio.run(main)
