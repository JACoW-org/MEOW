from asyncio import CancelledError
import logging

from typing import Optional

from redis.asyncio.client import PubSub

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
        logger.debug(f"subscribe >>>")

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
                logger.info(f"subscribe: Cancelled")
            except BaseException:
                logger.error("subscribe", exc_info=True)
            finally:
                if pubsub is not None:
                    logger.debug('pubsub.close()')
                    await pubsub.close()
        
        except CancelledError:
            logger.info(f"subscribe: Cancelled")
        except BaseException:
            logger.error("subscribe", exc_info=True)
          
                      
    async def __reader(self, p: PubSub):
        while app.state.webapp_running:
            try:
                async with create_task_group() as tg:
                    with move_on_after(2) as scope:
                        
                        logger.debug(f'__read')

                        payload = await p.get_message(
                            ignore_subscribe_messages=True,
                            timeout=1
                        )

                        # logger.debug(f"payload {payload}")

                        if payload and payload['type'] == 'message':
                            data = str(payload['data'], 'UTF-8')
                            # logger.debug(f"broadcast {data}")                               
                            await self._send(data)

                        await sleep(0.01)

            except BaseException:
                pass
           

    async def _send(self, message: str):
        try:
            
            payload: dict = json_decode(message)
            
            head: dict = payload.get('head', None)
            uuid: str = head.get('uuid', None)
            
            conn = app.active_connections.get(uuid, None)
            
            if conn is not None:
                await conn.send_text(message)
            else:
                logger.error(f"task_id: {uuid} have not a connection")
                
        except BaseException as e:
            logger.error("subscribe", e, exc_info=True)
