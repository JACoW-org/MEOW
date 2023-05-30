from dataclasses import dataclass

from meow.app.config import conf

import redis.asyncio as ar


@dataclass
class __Instances:
    """ """

    redis_client: ar.Redis


dbs = __Instances(
    redis_client=ar.Redis(
        host=conf.REDIS_SERVER_HOST,
        port=conf.REDIS_SERVER_PORT,
        client_name=conf.REDIS_CLIENT_NAME
    )
)
