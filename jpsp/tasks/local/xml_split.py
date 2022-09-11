"""
Split spms.xml into spms_summary.xml and sessions
"""

import asyncio
import logging
import pathlib

from anyio import open_file
from lxml import etree

from jpsp.tasks.infra.abstract_task import AbstractTask
from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse

logger = logging.getLogger(__name__)


async def main() -> None:
    """ Main Function """

    base_path = pathlib.Path(__file__).parent.parent.parent
    file_path = base_path.joinpath("static", "xml", "spms.xml")
    async with await open_file(file_path, mode='r', encoding="ISO-8859-1") as f:
        xml_str: bytes = (await f.read()).encode()

    root:etree._Element = etree.XML(xml_str)

    await asyncio.gather(*[
        write_child(base_path, child)
        for child in root
    ])


async def write_child(base_path: pathlib.Path, child: etree._Element) -> None:
    """ Write section to a separate file """

    abbr: str = child[0].get("abbr", "")
    print(child.tag, abbr)

    file_path = base_path.joinpath("static", "xml", f"{abbr}.xml")
    async with await open_file(file_path, mode='wb') as f:
        xml_str = str(etree.tostring(
            child,
            pretty_print=True,
            xml_declaration=True,
            encoding='iso-8859-1'
        )).encode()
        await f.write(xml_str)


class XmlSplitTask(AbstractTask):
    """ """

    async def run(self, req: TaskRequest, res: TaskResponse) -> None:
        await main()
