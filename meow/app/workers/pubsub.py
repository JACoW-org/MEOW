import asyncio
import logging
from typing import Callable, Optional

from redis.asyncio.client import PubSub

from anyio import create_task_group, move_on_after, sleep

from meow.app.config import conf

from meow.app.instances.databases import dbs
from meow.app.instances.application import app

from meow.app.workers.logic import AbsRedisWorkerLogicComponent
from meow.utils.serialization import json_encode

logger = logging.getLogger(__name__)


class PubsubRedisWorkerLogicComponent(AbsRedisWorkerLogicComponent):
    """ """

    def __init__(self):
        super().__init__('__pubsub_redis_worker_logic')


    async def subscribe(self, on_message: Callable):

        async def __read(p: PubSub):

            logger.debug('__read')
            
            # try:
            #     
            #     payload = await p.get_message(
            #         ignore_subscribe_messages=True,
            #         timeout=1
            #     )
            # 
            #     self.__log_payload(payload)
            # 
            #     return payload
            # 
            # except BaseException as e:
            #     pass
            # finally:
            #     await sleep(0.01)

            async with create_task_group() as tg:
                with move_on_after(2) as scope:
                    try:
                        
                        payload = await p.get_message(
                            ignore_subscribe_messages=True,
                            timeout=1
                        )
            
                        self.__log_payload(payload)
            
                        return payload
                
                    except BaseException as e:
                        pass
                    finally:
                        await sleep(0.01)
                        

        async def __reader(p: PubSub):
            while app.state.worker_running:
                payload = await __read(p)
                
                if payload and payload['type'] == 'message':
                    await on_message(payload['data'])
                
                # await anyio.sleep(0.01)


        async def __task():

            logger.debug(f"subscribe >>> topic: {conf.REDIS_CLIENT_NAME}")

            try:
                pubsub: Optional[PubSub] = dbs.redis_client.pubsub()
                try:
                    if pubsub is not None:
                        async with pubsub as p:
                            await p.subscribe(conf.REDIS_NODE_TOPIC)
                            
                            await __reader(p)
                            
                            logger.warning('### unsubscribe ###')
                            
                            await p.unsubscribe(conf.REDIS_NODE_TOPIC)

                except Exception as e:
                    logger.error(e, exc_info=True)
                finally:
                    if pubsub is not None:
                        logger.debug('pubsub.close()')
                        await pubsub.close()
            except Exception as e:
                logger.error(e, exc_info=True)

        return __task

    def __log_payload(self, payload: dict):
        logger.debug(f"REDIS NAME: {conf.REDIS_CLIENT_NAME}", )

        if payload:
            # data = payload['data']
            last_id = ''

            logger.debug(f"REDIS ID: {last_id}")
            # logger.debug(f"      --> {data}")
        else:
            logger.debug('Empty PAYLOAD')
