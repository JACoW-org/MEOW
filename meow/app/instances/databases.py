from dataclasses import dataclass
from typing import Any

from meow.app.config import conf

import redis.asyncio as ar


from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)


@dataclass
class __Instances:
    """ """

    redis_client: ar.Redis


dbs = __Instances(
    redis_client=ar.Redis(
        host=conf.REDIS_SERVER_HOST,
        port=conf.REDIS_SERVER_PORT,
        client_name=conf.REDIS_CLIENT_NAME,
        retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
        retry=Retry(ExponentialBackoff(), 3),  # type: ignore
        protocol=3
    )
)
