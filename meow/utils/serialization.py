from abc import ABC
from typing import Any, Callable


class AbstractSerializer(ABC):
    """ """

    def __init__(self, dumps: Callable, loads: Callable):
        self._dumps: Callable = dumps
        self._loads: Callable = loads


class JSONSerializer(AbstractSerializer):
    """ """

    def __init__(self):
        try:
            from orjson import dumps, loads
            super().__init__(dumps, loads)
        except ImportError:
            raise ImportError('Error: pip install orjson')

    def serialize(self, data: Any) -> bytes:
        return self._dumps(data)

    def deserialize(self, data: str) -> Any:
        return self._loads(data)


class PickleSerializer(AbstractSerializer):
    """ """

    def __init__(self):
        try:
            from pickle import dumps, loads
            super().__init__(dumps, loads)
        except ImportError:
            raise ImportError('Error: pip install pickle')

    def serialize(self, data: Any) -> bytes:
        return self._dumps(data)

    def deserialize(self, data: str) -> Any:
        return self._loads(data)


# class MsgPackSerializer(AbstractSerializer):
#     """ """
#
#     def __init__(self):
#         try:
#             from msgpack import dumps, loads
#             super().__init__(dumps, loads)
#         except ImportError:
#             raise ImportError('Error: pip install msgpack')
#
#     def serialize(self, data: Any) -> str:
#         return self._dumps(data)
#
#     def deserialize(self, data: str) -> Any:
#         return self._loads(data)


def json_encode(data: Any) -> bytes:
    return JSONSerializer().serialize(data)


def json_decode(data: str) -> Any:
    return JSONSerializer().deserialize(data)


def pickle_encode(data: Any) -> bytes:
    return PickleSerializer().serialize(data)
