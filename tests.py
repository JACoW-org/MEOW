import anyio

from tests.pikepdf.main_report import main
# from tests.hugo.generate import main


if __name__ == '__main__':
    anyio.run(main)
