import hashlib as hl

from typing import Any

from anyio.streams.file import FileReadStream

from meow.utils.serialization import pickle_encode


def sha1sum_hash(data: Any) -> str:
    return hl.sha1(pickle_encode(data)).hexdigest()


async def file_md5(file_path: str) -> str:
    md5_hash = hl.md5()

    async with await FileReadStream.from_path(file_path) as stream:
        async for chunk in stream:
            md5_hash.update(chunk)

    return md5_hash.hexdigest()

    # md5_hex = hl.md5(await file.read_bytes()).hexdigest()
    #
    # print(file_path, md5, md5_hex)

    # md5_hash = hl.md5()
    #
    # with open(file_path,"rb") as f:
    #     for chunk in iter(lambda: f.read(4096),b""):
    #         md5_hash.update(chunk) # type: ignore
    #
    # md5_hex = md5_hash.hexdigest()
    #
    # print(file_path, md5, md5_hex)

    # md5_hash = hl.md5()
    #
    # async with await open_file(file_path, "rb+") as f:
    #     async for chunk in f:
    #         md5_hash.update(chunk)
    #
    # md5_hex = md5_hash.hexdigest()
    #
    # print(file_path, md5, md5_hex)
