import logging as lg

from meow.tasks.infra.abstract_task import AbstractTask
from meow.tasks.infra.task_repository import TaskRepository


logger = lg.getLogger(__name__)


class TaskFactory:
    """ """

    @classmethod
    async def create_task(cls, code: str, args: dict) -> AbstractTask:
        """" """

        task_cls = await TaskRepository.get_task(code)

        logger.debug(f"create_task {code}")

        task_obj = task_cls(args)

        return task_obj
