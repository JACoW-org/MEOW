import abc
import logging
from typing import Callable


logger = logging.getLogger(__name__)


class AbsRedisWorkerLogicComponent():
    """ """

    def __init__(self, name: str):
        self.__init(name)

    def __init(self, name):
        self._name = name

    def create_logger(self) -> logging.Logger:
        return logging.getLogger(self._name)

    def exception_message(self) -> str:
        return f"{self._name} raised an exception"

    @abc.abstractmethod
    async def subscribe(self, on_message: Callable) -> Callable:
        pass

    @abc.abstractmethod
    async def publish(self, message: dict) -> None:
        pass
