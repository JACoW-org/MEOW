from abc import abstractmethod, ABC
from typing import Any

from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse


class AbstractTask(ABC):
    """ """

    def __init__(self, args: dict):
        """ """
        self.args = args

    @abstractmethod
    async def run(self, params: dict, context: dict = {}) -> Any:
        """ """
