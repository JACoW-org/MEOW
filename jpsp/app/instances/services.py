
import asyncio
import logging as lg

from dataclasses import dataclass
from jpsp.app.webapp import UvicornWebappManager

from jpsp.services.infra.redis import RedisManager

from jpsp.app.worker import RedisWorkerManager
from jpsp.app.socket import WebSocketManager

from jpsp.app.workers.pubsub import PubsubRedisWorkerLogicComponent

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
