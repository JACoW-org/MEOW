
import asyncio
import logging as lg

from dataclasses import dataclass
from meow.app.webapp import UvicornWebappManager

from meow.services.infra.redis import RedisManager

from meow.app.worker import RedisWorkerManager
from meow.app.socket import WebSocketManager

from meow.app.workers.pubsub import PubsubRedisWorkerLogicComponent

logger = lg.getLogger(__name__)


@dataclass
class __Instances:
    """ """

    redis_manager: RedisManager
    workers_manager: RedisWorkerManager
    webapp_manager: UvicornWebappManager
    socket_manager: WebSocketManager


srs = __Instances(
    redis_manager=RedisManager(),
    workers_manager=RedisWorkerManager(
        PubsubRedisWorkerLogicComponent()
    ),
    webapp_manager=UvicornWebappManager(),
    socket_manager=WebSocketManager()
)
