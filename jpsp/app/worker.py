import logging as lg

from datetime import datetime

from typing import Callable, Any

from jpsp.app.workers.logic import AbsRedisWorkerLogicComponent
from jpsp.tasks.infra.task_runner import TaskRunner

from anyio import create_task_group
from anyio import create_memory_object_stream

from anyio.streams.memory import MemoryObjectSendStream
from anyio.streams.memory import MemoryObjectReceiveStream
from anyio.streams.memory import WouldBlock

logger = lg.getLogger(__name__)


class RedisWorkerManager():
    """ """

    def __init__(self, logic: AbsRedisWorkerLogicComponent):
        self.logic: AbsRedisWorkerLogicComponent = logic


    async def run(self):

        logger.info('run - begin')
        
        sender, receiver = create_memory_object_stream(2)
        
        async with create_task_group() as tg:
            # listener
            tg.start_soon(self.start_listener, sender)
            # workers
            tg.start_soon(self.start_workers, receiver)
                              

        # async with create_task_group() as tg:
        #     with CancelScope(shield=True) as scope:
        #         
        #         async with sender:
        #             logger.info(f'start listener')
        #             await tg.start(self.subscribe_topic, sender.clone())
        #         
        #         async with receiver:
        #             for i in range(1, 8):
        #                 logger.info(f'start worker {i}')
        #                 await tg.start(self.process_task_worker, i, receiver.clone())
        #             
        #         tg.cancel_scope.cancel()

        logger.info('run - end')


    async def start_listener(self, sender: MemoryObjectSendStream):
        logger.debug('start_listener...')
        
        async with create_task_group() as tg:
            async with sender:
                tg.start_soon(self.subscribe_topic, sender.clone())
                
    
    async def start_workers(self, receiver: MemoryObjectReceiveStream):
        logger.debug('start_workers workers...')
        
        async with create_task_group() as tg:
            async with receiver:
                for i in range(8):
                    tg.start_soon(self.process_task_worker, i, receiver.clone())
            

    async def subscribe_topic(self, sender: MemoryObjectSendStream):
        """ """

        try:
            
            async with sender:
            
                async def on_message(data: Any):
                    logger.debug(f"######### __process data {data}")

                    # message = deserialize(data)
                    # logger.debug(f"__process message {message}")

                    try:
                        sender.send_nowait("exec_process")
                    except WouldBlock as e:
                        print(e)
                    # await self.queue.put("exec_process")

                __callable: Callable = await self.logic.subscribe(on_message=on_message)
            
                # self.task = create_task(
                #     __callable(),
                #     name=f'worker_task',
                #     logger=self.logic.create_logger(),
                #     message=self.logic.exception_message()
                # )
                
                async with create_task_group() as tg:
                    tg.start_soon(__callable)
        
        except BaseException as e:
            logger.error(f"Worker sub: Internal Error", exc_info=True)  
        

    async def process_task_worker(self, worker_id: int, receiver: MemoryObjectReceiveStream):
        """ """

        try:

            logger.debug(f"Worker {worker_id}: Waiting for task...")
            async with receiver:
                async for req in receiver:
                    await self.process_task_executor(worker_id, req)
        
        except BaseException:
            logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)  
    
    
    async def process_task_executor(self, worker_id: int, task: str):
        """ """

        try:

            logger.debug(f"Worker {worker_id}: Begin task {task}")

            start_time = datetime.now()

            await TaskRunner.run_task(task)

            logger.debug(
                f"Worker {worker_id}: End task {task} "
                f"{((datetime.now()) - start_time).total_seconds()}"
            )
            
        except BaseException as e:
            print(e)
            logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)


    # async def unsubscribe(self):
    #     logger.debug(f"unsubscribe >>> worker_group: 'worker_group'")
    #     if self.task is not None:
    #         cancel_task(self.task, logger)
    #         self.task = None
    # 
    # async def subscribe(self):
    #     if self.task is None:
    #         logger.debug(f"subscribe >>> worker_group: 'worker_group'")
    # 
    #         async def on_message(data: Any):
    #             logger.debug(f"######### __process data {data}")
    # 
    #             # message = deserialize(data)
    #             # logger.debug(f"__process message {message}")
    # 
    #             # await self.queue.put("exec_process")
    # 
    #         __callable: Callable = await self.logic.subscribe(on_message=on_message)
    #         
    #         self.task = create_task(
    #             __callable(),
    #             name=f'worker_task',
    #             logger=self.logic.create_logger(),
    #             message=self.logic.exception_message()
    #         )

    # async def publish(self, message: dict):
    #     await self.logic.publish(message)

