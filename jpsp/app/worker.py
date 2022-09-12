import uuid
import logging as lg

from datetime import datetime

from typing import Callable, Any

from jpsp.app.workers.logic import AbsRedisWorkerLogicComponent
from jpsp.tasks.infra.task_runner import TaskRunner

from anyio import create_task_group
from anyio import create_memory_object_stream
from anyio import to_thread

from anyio.from_thread import BlockingPortal

from anyio.streams.memory import MemoryObjectSendStream
from anyio.streams.memory import MemoryObjectReceiveStream
from anyio.streams.memory import WouldBlock

logger = lg.getLogger(__name__)


class RedisWorkerManager():
    """ """

    def __init__(self, logic: AbsRedisWorkerLogicComponent):
        self.logic: AbsRedisWorkerLogicComponent = logic

    async def run(self):

        # logger.info('run - begin')

        sender, receiver = create_memory_object_stream(4096)

        async with create_task_group() as tg:
            tg.start_soon(self.start_listener, sender)
            tg.start_soon(self.start_workers, receiver)

        # logger.info('run - end')

    async def start_listener(self, sender: MemoryObjectSendStream):
        # logger.debug('start_listener...')

        async with create_task_group() as tg:
            async with sender:
                tg.start_soon(self.subscribe_topic, sender.clone())

    async def start_workers(self, receiver: MemoryObjectReceiveStream):
        # logger.debug('start_workers workers...')

        async with create_task_group() as tg:
            async with receiver:
                for i in range(8):
                    tg.start_soon(self.process_task_worker,
                                  i, receiver.clone())

    # async def start_workers(self, receiver: MemoryObjectReceiveStream):
    #     logger.debug('start_workers workers...')
    #
    #     async with receiver:
    #
    #         logger.debug(f'start_workers receiver...')
    #
    #         async for task in receiver:
    #
    #             logger.debug(f'start_workers receiver... {task}')
    #
    #             params = dict()
    #             task_id = str(uuid.uuid4())
    #
    #             # limiter = CapacityLimiter(2)
    #             async with BlockingPortal() as portal:
    #
    #                 logger.debug(f'start_workers to_thread...')
    #
    #                 await to_thread.run_sync(
    #                     self.execute_in_thread,
    #                     portal, task_id, task, params,
    #                     # limiter=limiter
    #                 )

    # def execute_in_thread(self, portal: BlockingPortal, task_id: str, task: str, params: Any):
    #
    #     async def __task(task: str, params: Any):
    #
    #         start_time = datetime.now()
    #
    #         logger.info(
    #             f"Thread Pool: "
    #             f"Begin task {task} "
    #             f"Params {params} "
    #             f"{start_time} "
    #         )
    #
    #         await TaskRunner.send_begin(task_id=task_id, params=params)
    #
    #         result = await TaskRunner.run_task(task_id, task, params)
    #
    #         await TaskRunner.send_end(task_id=task_id, result=result)
    #
    #         end_time = datetime.now()
    #
    #         logger.info(
    #             f"Thread Pool: "
    #             f"End task {task} "
    #             f"Result {result} "
    #             f"{end_time} "
    #             f"{((end_time) - start_time).total_seconds()}"
    #         )
    #
    #     portal.start_task_soon(__task, task, params)

    async def subscribe_topic(self, sender: MemoryObjectSendStream):
        """ """

        try:

            async with sender:

                async def on_message(data: Any):
                    # logger.debug(f"######### __process data {data}")

                    # message = deserialize(data)
                    # logger.debug(f"__process message {message}")

                    try:
                        sender.send_nowait("event_ab")
                        await TaskRunner.send_queued(task_id="", params=dict())
                    except WouldBlock as error:
                        await TaskRunner.send_error(task_id="", error=error)
                        logger.error(f"Worker sub: queue limit", e, exc_info=True)

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
            logger.error(f"Worker sub: Internal Error", e, exc_info=True)

    async def process_task_worker(self, worker_id: int, receiver: MemoryObjectReceiveStream):
        """ """

        try:

            logger.debug(f"Worker {worker_id}: Waiting for task...")

            async with receiver:
                async for task in receiver:
                    await self.execute_in_worker_thread(worker_id, task, dict())

        except BaseException:
            logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)

    async def execute_in_current_thread(self, worker_id: int, task: str, params: dict):

        task_id = str(uuid.uuid4())
        
        await self.exec_in_loop(worker_id, task_id, task, params)

    async def execute_in_worker_thread(self, worker_id: int, task: str, params: dict):

        task_id = str(uuid.uuid4())

        def in_thread(portal: BlockingPortal, task: str):
            portal.start_task_soon(self.exec_in_loop, worker_id, task_id, task, params)

        async with BlockingPortal() as portal:
            await to_thread.run_sync(in_thread, portal, task)
            
    async def exec_in_loop(self, worker_id: int, task_id: str, task: str, params: dict):

        start_time = datetime.now()

        logger.debug(
            f"Worker Thread {worker_id}: "
            f"Begin task {task} "
        )
        
        try:
            await TaskRunner.send_begin(task_id=task_id, params=params)
            result = await TaskRunner.run_task(task_id, task, params)
            await TaskRunner.send_end(task_id=task_id, result=result)
        except BaseException as error:
            await TaskRunner.send_error(task_id=task_id, error=error)
        finally:
            logger.debug(
                f"Worker Thread {worker_id}: "
                f"End task {task} "
                f"{((datetime.now()) - start_time).total_seconds()}"
            )

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
