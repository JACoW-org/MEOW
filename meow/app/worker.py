import logging as lg

from asyncio import CancelledError

from datetime import datetime

from typing import Callable, Any

from meow.app.workers.logic import AbsRedisWorkerLogicComponent
from meow.tasks.infra.task_runner import TaskRunner

from anyio import CancelScope, create_task_group
from anyio import create_memory_object_stream
from anyio import to_thread

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
            tg.start_soon(self.begin_listener, sender)
            tg.start_soon(self.begin_workers, receiver)

        logger.debug('### run - end')

    async def begin_listener(self, sender: MemoryObjectSendStream):
        logger.debug('begin_listener...')

        with CancelScope(shield=True):
            async with sender:
                await self.subscribe_topic(sender.clone())

        logger.debug('end_listener...')

    async def begin_workers(self, receiver: MemoryObjectReceiveStream):
        logger.debug('begin_workers workers...')

        # with start_blocking_portal() as portal:
        #     futures = [
        #         portal.start_task_soon(self.process_task_worker,
        #                                i, receiver.clone())
        #         for i in range(1, 5)
        #     ]
        #
        #     for future in as_completed(futures):
        #         logger.debug(future.result())

        async with create_task_group() as tg:
            async with receiver:
                for i in range(2):
                    tg.start_soon(self.process_task_worker,
                                  i, receiver.clone())

        logger.debug('end_workers workers...')

    async def subscribe_topic(self, sender: MemoryObjectSendStream):
        """ """

        try:

            async with sender:

                async def on_message(raw: Any):

                    # logger.debug(f"######### __process data {raw}")

                    data: dict = json_decode(str(raw, 'utf-8'))

                    # logger.error(f"######### __process data {data}")

                    # {'code': 'task:exec', 'time': '1665050907325',
                    # 'uuid': '01GEPC94NXJGJ79YHYKSBRXJEA'}

                    head: dict = data.get('head', None)

                    if head:

                        code: str = head.get('code', None)
                        uuid: str = head.get('uuid', None)
                        time: str = head.get('time', None)

                        if not code:
                            logger.error("Invalid Code")

                        if code == 'task:kill':

                            logger.warn(f'KILL {code} {uuid}')

                            try:
                                # logger.info(f'kill {code} {uuid}')

                                await TaskRunner.kill_task(task_id=uuid)

                                logger.debug(tasks_cancel_scopes.keys())

                                if uuid in tasks_cancel_scopes:
                                    cancel_scope = tasks_cancel_scopes[uuid]
                                    cancel_scope.cancel()
                                    del tasks_cancel_scopes[uuid]
                                else:
                                    logger.debug('task_id noi in dictionary')

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

                                # logger.debug(f"######### sent -> {method}")

                                await TaskRunner.send_queued(task_id=uuid, task=method)

                            except WouldBlock as err:
                                await TaskRunner.send_error(task_id=uuid, task=method, error=err)
                                msg = "Worker sub: exausted"
                                logger.error(msg, exc_info=True)

                __callable: Callable = await self.logic.subscribe(on_message=on_message)

                await __callable()

        except CancelledError:
            logger.info("Worker sub: Cancelled")
        except BaseException:
            logger.error("Worker sub: Internal Error", exc_info=True)

    async def process_task_worker(self, worker_id: int, receiver: MemoryObjectReceiveStream):
        """ """

        try:

            logger.debug(f"Worker {worker_id}: Waiting for task...")

            async with receiver:
                async for raw in receiver:

                    async def _worker_cancel_task(scope: CancelScope):

                        task_id: str | None = None

                        try:
                            task = json_decode(raw)
                            task_id = task.get('task_id', None)

                            if task_id:
                                logger.debug(f"Worker {worker_id}: Begin")

                                tasks_cancel_scopes[task_id] = scope

                                method = task.get('method', None)
                                params = task.get('params', None)
                                context = task.get('context', None)

                                # await self.execute_in_current_thread(worker_id, method, params, context)
                                await self.execute_in_worker_thread(worker_id, method, params, context)

                                logger.debug(f"Worker {worker_id}: End")

                        except BaseException:
                            logger.error(f"Worker {worker_id}: Internal Error",
                                         exc_info=True)
                        finally:
                            try:
                                if task_id:
                                    if task_id in tasks_cancel_scopes:
                                        del tasks_cancel_scopes[task_id]
                            except BaseException as bex:
                                logger.error(bex, exc_info=True)

                    async with create_task_group() as tg:
                        with CancelScope():
                            tg.start_soon(_worker_cancel_task, tg.cancel_scope)

        except CancelledError:
            logger.info(f"Worker {worker_id}: Cancelled")
        except BaseException:
            logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)

    async def execute_in_current_thread(self, worker_id: int, method: str, params: dict, context: dict):
        await self.exec_in_loop(worker_id, method, params, context)

    async def execute_in_worker_thread(self, worker_id: int, method: str, params: dict, context: dict):
        def in_thread(portal: BlockingPortal):
            portal.start_task_soon(
                self.exec_in_loop, worker_id, method, params, context)

        async with BlockingPortal() as portal:
            await to_thread.run_sync(in_thread, portal, abandon_on_cancel=True)

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

            async for event in async_generator:
                event_type = event.get('type', '')
                event_value = event.get('value', None)

                if event_type == 'error':
                    await TaskRunner.send_error(task_id=task_id, task=method, error=event_value)
                elif event_type == 'result':
                    await TaskRunner.send_result(task_id=task_id, task=method, result=event_value)
                elif event_type == 'progress':
                    await TaskRunner.send_progress(task_id=task_id, task=method, progress=event_value)
                else:
                    await TaskRunner.send_log(task_id=task_id, task=method, log=event_value)

            await TaskRunner.send_end(task_id=task_id, task=method, result={})
        except BaseException as error:
            await TaskRunner.send_error(task_id=task_id, task=method, error=error)
        finally:
            logger.info(
                f"Worker Thread {worker_id}: "
                f"End task {method} "
                f"{((datetime.now()) - start_time).total_seconds()}"
            )
