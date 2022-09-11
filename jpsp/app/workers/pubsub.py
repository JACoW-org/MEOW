import asyncio
import logging
from typing import Callable, Optional

from redis.asyncio.client import PubSub

import anyio
import async_timeout

from jpsp.app.config import conf

from jpsp.app.instances.databases import dbs
from jpsp.app.instances.application import app

from jpsp.app.workers.logic import AbsRedisWorkerLogicComponent
from jpsp.utils.serialization import json_encode

logger = logging.getLogger(__name__)


class PubsubRedisWorkerLogicComponent(AbsRedisWorkerLogicComponent):
    """ """

    def __init__(self):
        super().__init__('__pubsub_redis_worker_logic')

    async def subscribe(self, on_message: Callable):

        async def __read(p: PubSub):

            # logger.debug('__read')

            try:
                async with async_timeout.timeout(2):
                    payload = await p.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1000
                    )

                    self.__log_payload(payload)

                    await anyio.sleep(0.01)

                    return payload

            except BaseException:
                pass

        async def __reader(p: PubSub):
            while app.state.running:
                payload = await __read(p)
                if payload and payload['type'] == 'message':
                    await on_message(payload['data'])

        async def __task():

            logger.info(f"subscribe >>> topic: {conf.REDIS_CLIENT_NAME}")

            try:
                pubsub: Optional[PubSub] = dbs.redis_client.pubsub()
                try:
                    if pubsub is not None:
                        async with pubsub as p:
                            await p.subscribe(conf.REDIS_NODE_TOPIC)
                            await __reader(p)
                            await p.unsubscribe(conf.REDIS_NODE_TOPIC)

                except Exception as e:
                    logger.error(e, exc_info=True)
                finally:
                    if pubsub is not None:
                        # logger.debug('pubsub.close()')
                        await pubsub.close()
            except Exception as e:
                logger.error(e, exc_info=True)

        return __task

    async def publish(self, message: dict):
        topic_name: str = await self.__publish_key()

        message_id = await dbs.redis_client.publish(
            channel=topic_name, message=json_encode(message)
        )

        logger.debug(f"publish_task {topic_name} {message_id}")

    async def __publish_key(self) -> str:
        counter: int = await dbs.redis_client.incr('workers:stream:counter')

        workers: list[str] = await self.__workers()
        topic_name: str = workers[counter % len(workers)]

        logger.debug(f"publish_key {topic_name} {counter} {workers}")

        return topic_name

    async def __workers(self):
        workers: list[str] = sorted(list(map(
            lambda w: str(w['name']),
            filter(
                lambda c: (str(c['name']).startswith('worker_')),
                await dbs.redis_client.client_list()
            )
        )))
        # logger.debug(f"__workers {workers} ")
        return workers

    def __log_payload(self, payload: dict):
        logger.debug(f"REDIS NAME: {conf.REDIS_CLIENT_NAME}", )

        if payload:
            data = payload['data']
            last_id = ''

            logger.debug(f"REDIS ID: {last_id}")
            logger.debug(f"      --> {data}")
        else:
            logger.debug('Empty PAYLOAD')


async def async_worker_stream_data_generator():
    """ """

    for i in range(6):
        await anyio.sleep(1)
        yield i


