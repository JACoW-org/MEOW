from dataclasses import dataclass
from typing import Any


@dataclass
class RedisIndexMeta:
    """ """

    index_key: str
    hash_key: str
    hash_val: str

    redis_schema: Any
    redis_definition: Any
