"""
Split spms.xml into spms_summary.xml and sessions
"""

import asyncio
import logging
import pathlib

from jpsp.tasks.infra.abstract_task import AbstractTask
from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse
from jpsp.utils.http import download_file

logger = logging.getLogger(__name__)


async def main() -> None:
    """ Main Function """

    # async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
    #     async with session.get('http://httpbin.org/get') as resp:
    #         print(resp.status)
    #         print(await resp.json())

    spms_full_url = "https://spms.kek.jp/pls/ipac19/spms.xml"
    spms_summary_url = "https://spms.kek.jp/pls/ipac19/spms_summary.xml"

    # spms_full_url = 'https://spms.kek.jp/pls/sap2017/spms.xml'
    # spms_summary_url = 'https://spms.kek.jp/pls/sap2017/spms_summary.xml'

    base_path = pathlib.Path(__file__).parent.parent.parent.parent
    xml_path = base_path.joinpath("static", "xml")

    xml_path.mkdir(exist_ok=True, parents=True)

    # spms_full_file = xml_path.joinpath("spms_full.xml")
    spms_summary_file = xml_path.joinpath("spms_summary.xml")

    await asyncio.gather(*[
        # download_file(spms_full_url, spms_full_file),
        download_file(spms_summary_url, spms_summary_file),
    ])

    # file_path = base_path.joinpath("static", "json", "httpbin.json")

    # bs = io.BytesIO()
    # async for chunk in fetch('http://httpbin.org/get'):
    #     bs.write(chunk)
    #
    # print(bs.getvalue())

    # json_serialize = ujson.dumps  # ujson fast serializer
    # timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes
    #
    # async with aiohttp.ClientSession(json_serialize=json_serialize, timeout=timeout) as session:
    #     async with session.get('http://httpbin.org/get') as resp:
    #         async with aiofiles.open(file_path, mode='wb') as fd:
    #             async for chunk in resp.content.iter_chunked(1024):
    #                 await fd.write(chunk)


class XmlDownloadTask(AbstractTask):
    """ """

    async def run(self, req: TaskRequest, res: TaskResponse) -> None:
        await main()
