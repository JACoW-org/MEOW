import anyio

from tests.pikepdf.main_pages import main
# from tests.hugo.generate import main


if __name__ == '__main__':
    anyio.run(main)
