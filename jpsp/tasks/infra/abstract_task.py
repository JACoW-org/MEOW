import logging as lg

from abc import abstractmethod, ABC
from typing import AsyncGenerator, Callable

from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse


logger = lg.getLogger(__name__)


class AbstractTask(ABC):
    """ """

    def __init__(self, args: dict):
        """ """
        self.args = args

    @abstractmethod
    async def run(self, params: dict, context: dict = {}) -> AsyncGenerator:
        """ """

