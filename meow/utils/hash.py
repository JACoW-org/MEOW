import hashlib as hl
from abc import ABC
from typing import Any, Callable

from meow.utils.serialization import pickle_encode


def sha1sum_hash(data: Any) -> str:
    return hl.sha1(pickle_encode(data)).hexdigest()
