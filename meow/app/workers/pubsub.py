import asyncio
import logging
from typing import Callable, Optional

from redis.asyncio.client import PubSub

from anyio import create_task_group, move_on_after, sleep

from meow.app.config import conf

from meow.app.instances.databases import dbs
from meow.app.instances.application import app

from meow.app.workers.logic import AbsRedisWorkerLogicComponent

from redis.exceptions import ConnectionError

logger = logging.getLogger(__name__)


class PubsubRedisWorkerLogicComponent(AbsRedisWorkerLogicComponent):
    """ """

    def __init__(self):
        super().__init__('__pubsub_redis_worker_logic')

    async def subscribe(self, on_message: Callable) -> Callable:

        async def __read(p: PubSub):

            logger.debug('__read')

            async with create_task_group():
                with move_on_after(delay=2, shield=True):
                    try:

                        payload = await p.get_message(
                            ignore_subscribe_messages=True,
                            timeout=5
                        )

                        self.__log_payload(payload)

                        return payload

                    except asyncio.exceptions.CancelledError:
                        logger.debug("__read:CancelledError",
                                     exc_info=False)
                    except ConnectionError:
                        logger.warn("__read:ConnectionError",
                                    exc_info=False)
                    except BaseException:
                        logger.error("__read:BaseException",
                                     exc_info=True)
                    finally:
                        await sleep(0.01)

        async def __reader(p: PubSub):
            while app.state.worker_running:
                try:
                    payload = await __read(p)

                    if payload and payload['type'] == 'message':
                        await on_message(payload['data'])

                    # await anyio.sleep(0.01)
                except asyncio.exceptions.CancelledError:
                    logger.debug("__reader:CancelledError")
                except ConnectionError:
                    logger.warning("__reader:ConnectionError",
                                   exc_info=False)

            logger.warning(
                f"app.state.worker_running: {app.state.worker_running}")

        async def __task():

            logger.debug(f"subscribe >>> topic: {conf.REDIS_CLIENT_NAME}")

            try:
                pubsub: Optional[PubSub] = dbs.redis_client.pubsub(
                    push_handler_func=lambda x: x
                )

                try:
                    if pubsub is not None:
                        async with pubsub as p:
                            await p.subscribe(conf.REDIS_NODE_TOPIC)

                            await __reader(p)

                            logger.warning('### unsubscribe ###')

                            await p.unsubscribe(conf.REDIS_NODE_TOPIC)

                except asyncio.CancelledError:
                    logger.info("__task:CancelledError")
                except ConnectionError:
                    logger.warn("__task:ConnectionError",
                                exc_info=False)
                except BaseException as be:
                    logger.error(be, exc_info=True)
                finally:
                    if pubsub is not None:
                        logger.debug('pubsub.close()')
                        await pubsub.close()

            except BaseException as e:
                logger.error(e, exc_info=True)

        return __task

    def __log_payload(self, payload: dict | None):
        logger.debug(f"\n\nREDIS NAME: {conf.REDIS_CLIENT_NAME}", )

        if payload:
            # data = payload['data']
            last_id = ''

            logger.debug(f"REDIS ID: {last_id}")
            # logger.debug(f"      --> {data}")
        else:
            logger.debug('Empty PAYLOAD')
