from asyncio import CancelledError
import logging as lg

import signal

from datetime import datetime

from typing import Callable, Any

from meow.app.workers.logic import AbsRedisWorkerLogicComponent
from meow.tasks.infra.task_runner import TaskRunner

from anyio import CancelScope, create_task_group
from anyio import create_memory_object_stream
from anyio import to_thread

from anyio.abc import TaskStatus

from anyio.from_thread import BlockingPortal

from anyio.streams.memory import MemoryObjectSendStream
from anyio.streams.memory import MemoryObjectReceiveStream
from anyio.streams.memory import WouldBlock

from meow.utils.serialization import json_decode, json_encode

logger = lg.getLogger(__name__)



tasks_cancel_scopes: dict[str, CancelScope] = dict()



class RedisWorkerManager():
    """ """
    
    

    def __init__(self, logic: AbsRedisWorkerLogicComponent):
        self.logic: AbsRedisWorkerLogicComponent = logic

    async def run(self):

        logger.debug('### run - begin')

        sender, receiver = create_memory_object_stream(4096)

        async with create_task_group() as tg:
            tg.start_soon(self.start_listener, sender)
            tg.start_soon(self.start_workers, receiver)

        logger.debug('### run - end')

    async def start_listener(self, sender: MemoryObjectSendStream):
        logger.debug('start_listener...')

        async with create_task_group() as tg:
            async with sender:
                tg.start_soon(self.subscribe_topic, sender.clone())

        logger.debug('close_listener...')

    async def start_workers(self, receiver: MemoryObjectReceiveStream):
        logger.debug('start_workers workers...')

        async with create_task_group() as tg:
            async with receiver:
                for i in range(2):
                    tg.start_soon(self.process_task_worker,
                                   i, receiver.clone())

        logger.debug('close_workers workers...')

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

                async def on_message(raw: Any):

                    # logger.debug(f"######### __process data {raw}")

                    data: dict = json_decode(str(raw, 'utf-8'))

                    # logger.debug(f"######### __process data {data}")

                    # {'code': 'task:exec', 'time': '1665050907325', 'uuid': '01GEPC94NXJGJ79YHYKSBRXJEA'}

                    head: dict = data.get('head', None)

                    if head is not None:

                        code: str = head.get('code', None)
                        uuid: str = head.get('uuid', None)
                        time: str = head.get('time', None)
                        
                        if code == 'task:kill':
                            
                            logger.error(f'KILLLLLLLLLLLLLLLL {code} {uuid}')

                            try:
                                # logger.info(f'kill {code} {uuid}')
                                
                                await TaskRunner.kill_task(task_id=uuid)
                                
                                logger.error(tasks_cancel_scopes.keys())
                                
                                if uuid in tasks_cancel_scopes:
                                    cancel_scope = tasks_cancel_scopes[uuid] 
                                    cancel_scope.cancel()
                                    del tasks_cancel_scopes[uuid] 
                                else:
                                    logger.error('task_id noi in dictionary')
                                
                            except BaseException as bex:
                                logger.error(bex, exc_info=True)

                        body: dict = data.get('body', {})
                        method: str = body.get('method', None)
                        params: dict = body.get('params', None)

                        if code == 'task:exec':

                            try:

                                context = {
                                    'code': code,
                                    'uuid': uuid,
                                    'time': time
                                }

                                sender.send_nowait(json_encode({
                                    'task_id': uuid,
                                    'method': method,
                                    'params': params,
                                    'context': context,
                                }))

                                logger.debug(f"######### sent -> {method}")

                                await TaskRunner.send_queued(task_id=uuid, task=method)

                            except WouldBlock as err:
                                await TaskRunner.send_error(task_id=uuid, task=method, error=err)
                                msg = f"Worker sub: exausted"
                                logger.error(msg, err, exc_info=True)

                __callable: Callable = await self.logic.subscribe(on_message=on_message)

                await __callable()

        except CancelledError:
            logger.info(f"Worker sub: Cancelled")
        except BaseException as e:
            logger.error(f"Worker sub: Internal Error", exc_info=True)

    async def process_task_worker(self, worker_id: int, receiver: MemoryObjectReceiveStream):
        """ """

        try:

            logger.debug(f"Worker {worker_id}: Waiting for task...")

            async with receiver:
                async for raw in receiver:
                    
                    async def _cancel_task(scope: CancelScope):
                        
                        task_id: str | None = None
                        
                        try:
                            task = json_decode(raw)
                            task_id = task.get('task_id', None)
                            
                            if task_id is not None:
                                logger.debug(f"Worker {worker_id}: Begin")
                                
                                tasks_cancel_scopes[task_id] = scope
                                
                                method = task.get('method', None)
                                params = task.get('params', None)
                                context = task.get('context', None)

                                await self.execute_in_current_thread(worker_id, method, params, context)
                                # await self.execute_in_worker_thread(worker_id, method, params, context)

                                logger.debug(f"Worker {worker_id}: End")

                        except BaseException:
                            logger.error(
                                f"Worker {worker_id}: Internal Error", exc_info=True)
                        finally:
                            try:
                                if task_id is not None:
                                    if task_id in tasks_cancel_scopes:
                                        del tasks_cancel_scopes[task_id]
                            except BaseException as bex:
                                logger.error(bex, exc_info=True)
                    
                    
                    async with create_task_group() as tg:
                        with CancelScope() as scope:
                            tg.start_soon(_cancel_task, tg.cancel_scope)


        except CancelledError:
            logger.info(f"Worker {worker_id}: Cancelled")
        except BaseException:
            logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)

    async def execute_in_current_thread(self, worker_id: int, method: str, params: dict, context: dict):
        await self.exec_in_loop(worker_id, method, params, context)

    async def execute_in_worker_thread(self, worker_id: int, method: dict, params: dict, context: dict):
        def in_thread(portal: BlockingPortal):
            portal.start_task_soon(
                self.exec_in_loop, worker_id, method, params, context)

        async with BlockingPortal() as portal:
            await to_thread.run_sync(in_thread, portal)

    async def exec_in_loop(self, worker_id: int, method: str, params: dict, context: dict):

        start_time = datetime.now()

        task_id: str = context.get('uuid', None)

        logger.info(
            f"Worker Thread {worker_id}: "
            f"Begin task {method} "
        )

        try:
            await TaskRunner.send_begin(task_id=task_id, task=method)

            async_generator = TaskRunner.run_task(
                task_id, method, params, context)

            async for result in async_generator:
                result_type = result.get('type', '')
                result_value = result.get('value', None)

                if result_type == 'result':
                    await TaskRunner.send_result(task_id=task_id, task=method, result=result_value)
                elif result_type == 'progress':
                    await TaskRunner.send_progress(task_id=task_id, task=method, progress=result_value)
                else:
                    await TaskRunner.send_log(task_id=task_id, task=method, log=result_value)

            await TaskRunner.send_end(task_id=task_id, task=method, result={})
        except BaseException as error:
            await TaskRunner.send_error(task_id=task_id, task=method, error=error)
        finally:
            logger.info(
                f"Worker Thread {worker_id}: "
                f"End task {method} "
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
