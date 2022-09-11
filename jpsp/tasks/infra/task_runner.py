import logging
import uuid

from jpsp.tasks.infra.task_factory import TaskFactory
from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse

logger = logging.getLogger(__name__)


class TaskRunner:
    """ """

    @classmethod
    async def run_task(cls, code: str) -> None:
        """ """

        try:
            task_id = uuid.uuid4()

            args = dict(
                task_id=task_id
            )

            req = TaskRequest()
            res = TaskResponse()

            logger.debug(f"run_task {code} {args}")

            task_obj = await TaskFactory.create_task(code, args)

            logger.debug(f"run_task - task created")

            await task_obj.run(req, res)
        except Exception:
            logger.error("subscribe", exc_info=True)
