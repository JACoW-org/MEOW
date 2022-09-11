import logging

from jpsp.tasks.infra.abstract_task import AbstractTask
from jpsp.tasks.infra.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskFactory:
    """ """

    @classmethod
    async def create_task(cls, code: str, args: dict) -> AbstractTask:
        """" """

        task_cls = await TaskRepository.get_task(code)

        logging.debug(f"create_task {code}")

        task_obj = task_cls(args)

        return task_obj
