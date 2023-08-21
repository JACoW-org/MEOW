from anyio import run

# from tests.pikepdf.main_report import main
# from tests.hugo.generate import main
# from tests.dataclass.main import main
# from tests.xml.main import main
# from tests.group.main import main
# from tests.xmp.main import main



async def main():

    import string
    ascii = list(string.ascii_uppercase)

    for index in range(16):

        conv = "".join([ascii[int(char)] for char in "{:06d}".format(index)])

        print(conv)


if __name__ == '__main__':
    run(main)
