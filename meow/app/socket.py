import logging

from typing import Optional

from asyncio.exceptions import CancelledError

from redis.asyncio.client import PubSub
from redis.exceptions import ConnectionError

from anyio import create_task_group, move_on_after, sleep

from meow.app.instances.databases import dbs
from meow.app.instances.application import app

from meow.utils.serialization import json_decode

logger = logging.getLogger(__name__)


class WebSocketManager():
    """ """

    async def run(self):
        await self.__task()

    async def __task(self):
        logger.debug("subscribe >>>")

        try:

            pubsub: Optional[PubSub] = dbs.redis_client.pubsub()

            try:
                if pubsub is not None:
                    async with pubsub as p:
                        # logger.debug('subscribe -- meow:feed')
                        await p.subscribe("meow:feed")
                        await self.__reader(p)
                        # logger.debug('unsubscribe -- meow:feed')
                        await p.unsubscribe("meow:feed")

            except CancelledError:
                logger.info("subscribe: Cancelled")
            except ConnectionError:
                logger.info("subscribe: Disconnected")
            except BaseException:
                logger.error("subscribe", exc_info=True)
            finally:
                if pubsub is not None:
                    logger.debug('pubsub.close()')
                    await pubsub.close()

        except CancelledError:
            logger.info("subscribe: Cancelled")
        except ConnectionError:
            logger.info("subscribe: Disconnected")
        except BaseException:
            logger.error("subscribe", exc_info=True)

    async def __reader(self, p: PubSub):
        while app.state.webapp_running:
            try:
                async with create_task_group():
                    with move_on_after(delay=2, shield=True):

                        logger.debug('__read')

                        try:
                            payload = await p.get_message(
                                ignore_subscribe_messages=True,
                                timeout=5
                            )

                            # logger.debug(f"payload {payload}")

                            if payload and payload['type'] == 'message':
                                data = str(payload['data'], 'UTF-8')
                                # logger.debug(f"broadcast {data}")
                                await self._send(data)

                        except CancelledError:
                            logger.debug("__reader: CancelledError")
                        except ConnectionError:
                            logger.warn("__reader: ConnectionError")
                        except BaseException:
                            logger.error("__reader", exc_info=True)

                        await sleep(0.01)

            except CancelledError:
                logger.debug("__reader:CancelledError")
            except ConnectionError:
                logger.warn("__reader: ConnectionError")
            except BaseException:
                logger.error("__reader", exc_info=True)

    async def _send(self, message: str):
        try:

            if message:

                payload: dict = json_decode(message)

                head: dict | None = payload.get(
                    'head', None) if payload else None
                uuid: str | None = head.get('uuid', None) if head else None
                conn = app.active_connections.get(uuid, None) if uuid else None

                await conn.send_text(message) if conn else None

        except BaseException as e:
            logger.error(message)
            logger.error("subscribe", e, exc_info=True)
