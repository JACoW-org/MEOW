import logging as lg

from abc import abstractmethod, ABC

from typing import AsyncGenerator
from meow.app.errors.service_error import ServiceError
from meow.tasks.infra.task_status import TaskStatus


logger = lg.getLogger(__name__)


class AbstractTask(ABC):
    """ """

    def __init__(self, code: str, task_id: str):
        """ """
        self.code = code
        self.task_id = task_id

    def assert_is_running(self) -> None:
        """ """

        # TaskStatus.print()

        # is_running = TaskStatus.is_running(self.task_id)

        # logger.warning(f"task_id: {self.task_id} - is_running: {is_running}")

        if not TaskStatus.is_running(self.task_id):
            raise ServiceError(f"task_id {self.task_id} killed")

        # logger.warning(f"task_id: {self.task_id} - is_running: {is_running}")

    @abstractmethod
    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator:
        """ """
