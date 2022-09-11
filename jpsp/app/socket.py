import logging

from typing import  Optional

from redis.asyncio.client import PubSub

from anyio import create_task_group, move_on_after, sleep

from jpsp.app.instances.databases import dbs
from jpsp.app.instances.application import app

from anyio import create_task_group

logger = logging.getLogger(__name__)


class WebSocketManager():
    """ """
        
    async def run(self):
        
        async def __reader(p: PubSub):
            while app.state.running:
                try:
                    async with create_task_group() as tg:
                        with move_on_after(2) as scope:
                            logger.debug('__read')

                            payload = await p.get_message(
                                ignore_subscribe_messages=True,
                                timeout=1000
                            )

                            logger.debug(f"payload {payload}")

                            if payload and payload['type'] == 'message':
                                data = str(payload['data'], 'UTF-8')
                                logger.debug(f"broadcast {data}")
                                await self.broadcast(data)

                            await sleep(0.01)

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
                        logger.debug('pubsub.close()')
                        await pubsub.close()
                    
            except BaseException:
                logger.error("subscribe", exc_info=True)
            
        async with create_task_group() as tg:
            tg.start_soon(__task)
                

    # async def unsubscribe(self):
    #     logger.debug(f"unsubscribe >>> worker_group: 'worker_group'")
    #     if self.task is not None:
    #         cancel_task(self.task, logger)
    #         self.task = None

    # async def subscribe(self):
# 
    #     if self.task is None:
# 
    #         async def __reader(p: PubSub):
    #             while app.state.running:
    #                 try:
    #                     async with async_timeout.timeout(2):
    #                         logger.debug('__read')
# 
    #                         payload = await p.get_message(
    #                             ignore_subscribe_messages=True,
    #                             timeout=1000
    #                         )
# 
    #                         logger.debug(f"payload {payload}")
# 
    #                         if payload and payload['type'] == 'message':
    #                             data = str(payload['data'], 'UTF-8')
    #                             logger.debug(f"broadcast {data}")
    #                             await self.broadcast(data)
# 
    #                         await anyio.sleep(0.01)
# 
    #                 except BaseException:
    #                     pass
# 
    #         async def __task():
# 
    #             logger.debug(f"subscribe >>>")
# 
    #             try:
# 
    #                 pubsub: Optional[PubSub] = dbs.redis_client.pubsub()
# 
    #                 try:
# 
    #                     if pubsub is not None:
    #                         async with pubsub as p:
    #                             await p.subscribe("chat:c")
    #                             await __reader(p)
    #                             await p.unsubscribe("chat:c")
# 
    #                 except BaseException:
    #                     logger.error("subscribe", exc_info=True)
    #                 finally:
    #                     if pubsub is not None:
    #                         logger.debug('pubsub.close()')
    #                         await pubsub.close()
    #                     
    #             except BaseException:
    #                 logger.error("subscribe", exc_info=True)
# 
    #         # self.task = create_task(
    #         #     __task(),
    #         #     name=f'websocket_task',
    #         #     logger=logging.getLogger('__task'),
    #         #     message="__task raised an exception"
    #         # )
    #          
    #         async with create_task_group() as tg:
    #             tg.start_soon(__task)


    # async def connect(self, websocket: WebSocket):
    #     app.active_connections.append(websocket)

    # async def disconnect(self, websocket: WebSocket):
    #     app.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in app.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError:
                pass

