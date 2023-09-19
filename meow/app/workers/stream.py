import logging
from typing import Any, Callable

import anyio

from meow.app.config import conf

from meow.app.instances.application import app
from meow.app.instances.databases import dbs

from meow.app.workers.logic import AbsRedisWorkerLogicComponent
from meow.utils.serialization import json_encode

logger = logging.getLogger(__name__)


class StreamRedisWorkerLogicComponent(AbsRedisWorkerLogicComponent):
    """ """

    def __init__(self):
        super().__init__('__stream_redis_worker_logic')

    async def subscribe(self, on_message: Callable) -> Callable:

        async def __read():
            try:
                payload = await dbs.redis_client.xreadgroup(
                    groupname='worker_group',
                    consumername=conf.REDIS_CLIENT_NAME,
                    streams={'worker_stream': '>'},
                    block=10000,
                    count=1,
                )

                self.__log_payload(payload)

                return payload
            except BaseException:
                pass

        async def __task():

            await self.__ensure_stream()

            try:

                logger.info("subscribe >>> worker_group: 'worker_group'")

                while app.state.worker_running:
                    payload = await __read()
                    if payload:
                        key, messages = payload[0]
                        last_id, data = messages[0]
                        await on_message(data)
                    await anyio.sleep(0)

            except Exception as e:
                logger.error(e, exc_info=True)

        return __task

    async def publish(self, message: dict) -> None:
        stream_key: str = await self.__publish_key()
        fields: Any = dict(data=json_encode(message))

        message_id = await dbs.redis_client.xadd(
            name=stream_key,
            fields=fields,
            maxlen=1000
        )

        logger.debug(f"publish_task {stream_key} {message_id}")

    async def __publish_key(self) -> str:
        return 'worker_stream'

    async def __ensure_stream(self):

        async def __stream_exists() -> bool:
            stream_exists: int = await dbs.redis_client.exists('worker_stream')
            logger.debug(f"stream_exists {stream_exists}")
            return stream_exists == 1

        async def __create_group():
            create_group = await dbs.redis_client.xgroup_create(
                name='worker_stream',
                groupname='worker_group',
                mkstream=True,
                id='$'
            )
            # logger.debug(f"create_group {create_group}")
            return create_group

        async def __groups_list():
            groups_info = await dbs.redis_client.xinfo_groups(
                name='worker_stream')
            groups = [str(x['name'], 'UTF-8') for x in groups_info]
            # logger.debug(f"groups {groups}")
            return groups

        try:
            if not await __stream_exists():
                await __create_group()
            else:
                if 'worker_group' not in await __groups_list():
                    await __create_group()
        except Exception as e:
            logger.error(e, exc_info=True)

    def __log_payload(self, payload: dict):
        if payload:
            key, messages = payload[0]
            last_id, data = messages[0]

            logger.debug(f"\n\nREDIS NAME: {conf.REDIS_CLIENT_NAME}", )
            logger.debug(f"REDIS ID: {last_id}")
            # logger.debug(f"      --> {data}")


def create_logic():
    return StreamRedisWorkerLogicComponent()
