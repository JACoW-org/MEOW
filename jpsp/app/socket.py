import asyncio
import logging
from typing import List, Optional

from redis.asyncio.client import PubSub

import anyio
import async_timeout

from starlette.websockets import WebSocket

from jpsp.app.instances.databases import dbs
from jpsp.app.instances.application import app

from jpsp.utils.task_exception import create_task, cancel_task

logger = logging.getLogger(__name__)


class WebSocketManager():
    """ """

    def __init__(self):
        self.task: Optional[asyncio.Task] = None
        self.active_connections: List[WebSocket] = []

    async def unsubscribe(self):
        logger.debug(f"unsubscribe >>> worker_group: 'worker_group'")
        if self.task is not None:
            cancel_task(self.task, logger)
            self.task = None

    async def subscribe(self):

        if self.task is None:

            async def __reader(p: PubSub):
                while app.state.running:
                    try:
                        async with async_timeout.timeout(2):
                            # logger.debug('__read')

                            payload = await p.get_message(
                                ignore_subscribe_messages=True,
                                timeout=1000
                            )

                            logger.debug(f"payload {payload}")

                            if payload and payload['type'] == 'message':
                                data = str(payload['data'], 'UTF-8')
                                logger.debug(f"broadcast {data}")
                                await self.broadcast(data)

                            await anyio.sleep(0.01)

                    except BaseException:
                        pass

            async def __task():

                logger.debug(f"subscribe >>>")

                try:

                    pubsub: Optional[PubSub] = dbs.redis_client.pubsub()

                    try:

                        if pubsub is not None:
                            async with pubsub as p:
                                await p.subscribe("chat:c")
                                await __reader(p)
                                await p.unsubscribe("chat:c")

                    except BaseException:
                        logger.error("subscribe", exc_info=True)
                    finally:
                        if pubsub is not None:
                            await pubsub.close()
                        
                except BaseException:
                    logger.error("subscribe", exc_info=True)

            self.task = create_task(
                __task(),
                name=f'websocket_task',
                logger=logging.getLogger('__task'),
                message="__task raised an exception"
            )

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError:
                pass

