"""
Merge spms_summary.xml and sessions
"""

# import asyncio
# import logging
# import pathlib
# from typing import Any, Optional
# 
# from anyio import open_file
# from lxml import etree
# 
# from meow.tasks.infra.abstract_task import AbstractTask
# from meow.tasks.infra.task_request import TaskRequest
# from meow.tasks.infra.task_response import TaskResponse
# from meow.tasks.local.xml_download import download_file
# from meow.utils.process import execute_process
# 
# logger = logging.getLogger(__name__)
# 
# 
# async def process_child(xml_path: pathlib.Path, child: etree._Element) -> Optional[etree._Element]:
#     await download_child(xml_path, child)
#     # await fix_child(xml_path, child)
#     return await read_child(xml_path, child)
# 
# 
# async def fix_child(xml_path: pathlib.Path, child: etree._Element) -> None:
#     """ Read section from file """
# 
#     abbr: str = child[0].get("abbr", "")
# 
#     print("fix_child -->", child.tag, abbr)
# 
#     temp_path = xml_path.joinpath(f"{abbr}_temp.xml")
#     file_path = xml_path.joinpath(f"{abbr}.xml")
# 
#     # xmllint --format get_xml/XML/spms_broken.xml
#     # --output get_xml/XML/spms.xml
#     # --nowarning --recover --quiet
# 
#     result = await execute_process([
#         "xmllint", f"{temp_path}",
#         "--format", "--recover",
#         "--output", f"{file_path}"
#     ])
# 
#     logger.debug(result)
# 
#     temp_path.unlink(missing_ok=True)
# 
# 
# async def download_child(xml_path: pathlib.Path, child: etree._Element) -> None:
#     """ Read section from file """
# 
#     abbr: str = child[0].get("abbr", "")
# 
#     print("download_child -->", child.tag, abbr)
# 
#     file_url = f"https://spms.kek.jp/pls/ipac19/xml2.session_data?sid={abbr}"
# 
#     file_path = xml_path.joinpath(f"{abbr}.xml")
# 
#     await download_file(file_url, file_path)
# 
# 
# async def read_child(xml_path: pathlib.Path, child: etree._Element) -> Optional[etree._Element]:
#     """ Read section from file """
# 
#     try:
# 
#         abbr: str = child[0].get("abbr", "")
# 
#         print("read_child -->", child.tag, abbr)
# 
#         file_path = xml_path.joinpath(f"{abbr}.xml")
# 
#         async with await open_file(file_path, mode='r', encoding="ISO-8859-1") as f:
#             xml_str: bytes = (await f.read()).encode()
# 
#         root: etree._Element = etree.XML(xml_str,
#                                         etree.XMLParser(encoding='iso-8859-1', recover=True))
#         return root
# 
#     except Exception as e:
#         logger.error(e)
# 
#     return None
# 
# 
# class XmlMergeTask(AbstractTask):
#     """ """
# 
#     async def run(self, params: Any) -> Any:
#         """ Main Function """
# 
#         summary_url = "https://spms.kek.jp/pls/ipac19/spms_summary.xml"
# 
#         base_path = pathlib.Path(__file__).parent.parent.parent.parent
#         xml_path = base_path.joinpath("static", "xml")
#         summary_path = xml_path.joinpath("spms_summary.xml")
# 
#         xml_path.mkdir(exist_ok=True, parents=True)
# 
#         await download_file(summary_url, summary_path)
# 
#         if not summary_path.exists():
#             raise Exception(f"{summary_path} not found")
# 
#         async with await open_file(summary_path, mode='r', encoding="ISO-8859-1") as f:
#             xml_str: bytes = (await f.read()).encode()
# 
#         root: etree._Element = etree.XML(xml_str)
#         attrib = {k: root.get(k) for k in root.keys()}
# 
#         # print(attrib)
# 
#         new_root = etree.Element(root.tag, attrib=attrib)  # type: ignore
# 
#         results = await asyncio.gather(*[
#             process_child(xml_path, child)
#             for child in root
#         ])
# 
#         for result in results:
#             if result:
#                 new_root.append(result)
# 
#         # await asyncio.gather(*[
#         #     download_child(xml_path, child)
#         #     for child in root
#         # ])
#         #
#         # await asyncio.gather(*[
#         #     fix_child(xml_path, child)
#         #     for child in root
#         # ])
#         #
#         # results = await asyncio.gather(*[
#         #     read_child(xml_path, child)
#         #     for child in root
#         # ])
#         #
#         # for result in results:
#         #     new_root.append(result)
# 
#         # for child in root:
#         #     await download_child(xml_path, child)
#         #
#         # for child in root:
#         #     await fix_child(xml_path, child)
#         #
#         # for child in root:
#         #     new_root.append(
#         #         await read_child(xml_path, child)
#         #     )
# 
#         new_path = xml_path.joinpath("spms.xml")
#         async with await open_file(new_path, mode='wb') as f:
#             xml_str = str(etree.tostring(
#                 new_root,
#                 pretty_print=True,
#                 xml_declaration=True,
#                 encoding='iso-8859-1'
#             )).encode()
#             await f.write(xml_str)
# 
#         return True
