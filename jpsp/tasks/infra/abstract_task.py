from abc import abstractmethod, ABC

from jpsp.tasks.infra.task_request import TaskRequest
from jpsp.tasks.infra.task_response import TaskResponse


class AbstractTask(ABC):
    """ """

    def __init__(self, args: dict):
        """ """
        self.args = args

    @abstractmethod
    async def run(self, req: TaskRequest, res: TaskResponse) -> None:
        """ """
