"""
Split spms.xml into spms_summary.xml and sessions
"""

# import logging
# import pathlib
# from typing import Any
# 
# from jpsp.tasks.infra.abstract_task import AbstractTask
# from jpsp.tasks.infra.task_request import TaskRequest
# from jpsp.tasks.infra.task_response import TaskResponse
# from jpsp.utils.process import execute_process
# 
# logger = logging.getLogger(__name__)
# 
# 
# class ExecProcessTask(AbstractTask):
#     """ """
# 
#     async def run(self, params: Any) -> Any:
# 
#         logger.info("exec_program:status:start")
# 
#         # await asyncio.sleep(30)
# 
#         base_path = pathlib.Path(__file__).parent.parent.parent.parent
#         xml_path = base_path.joinpath("static", "xml")
# 
#         logger.info("exec_program:status:run_first_cmd")
# 
#         result = await execute_process(
#             ["ls", "-lh", f"{xml_path}"]
#         )
# 
#         # logger.debug(result)
# 
#         logger.info("exec_program:status:run_second_cmd")
# 
#         result = await execute_process(
#             ["sleep", "5"]
#         )
# 
#         # logger.debug(result)
# 
#         logger.info(f"exec_program:status:end")
# 
#         return True
