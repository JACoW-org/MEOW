import asyncio
import logging
import signal

from asyncio import Task
from typing import Any


from anyio import TASK_STATUS_IGNORED, create_task_group
from anyio.abc import TaskStatus

from meow.models.infra.locks import RedisLockList
from meow.utils.http import HttpClientSessions
from meow.utils.task_exception import create_task

from meow.app.instances.application import app


logger = logging.getLogger(__name__)


async def create_task_queue():

    async def _create_task_group():
        async with create_task_group() as tg:
            for i in range(1, 2):
                logger.info(f'start worker {i}')
                await tg.start(process_task_worker, i)

    create_task(
        _create_task_group(),
        name='create_task_group',
        logger=logging.getLogger("process_task_worker"),
        message="process_task_worker raised an exception",
    )


async def process_task_worker(worker_id: int, task_status: TaskStatus =
                              TASK_STATUS_IGNORED):
    """ """

    try:
        task_status.started()

        while app.state.worker_running:
            await process_task_executor(worker_id)

    except BaseException:
        logger.error(f"Worker {worker_id}: Internal Error", exc_info=True)


async def process_task_executor(worker_id: int):
    """ """
    pass
#    try:
#        logger.debug(f"Worker {worker_id}: Waiting for task...")
#
#        task = await srs.workers_manager.queue.get()
#
#        logger.debug(f"Worker {worker_id}: Begin task {task}")
#
#        start_time = datetime.now()
#
#        await TaskRunner.run_task(task)
#
#        logger.debug(
#            f"Worker {worker_id}: End task {task} "
#            f"{((datetime.now()) - start_time).total_seconds()}"
#        )
#
#        srs.workers_manager.queue.task_done()
#
#    except BaseException as e:
#        logger.error(f"Worker {worker_id}: Internal Error", e, exc_info=True)


async def create_signals_handler():
    """ """

    def cancel_task(task: Task):
        try:
            if task.get_name().startswith('queue_task_'):
                logger.info(f'Killing task {task.get_name()}')
                task.cancel()
        except Exception as e:
            logger.error(f'Error killing task {task.get_name()}')
            logger.error(e)

    async def shutdown(sig: Any):
        """try to shut down gracefully"""

        await RedisLockList.release_all_locks()
        await HttpClientSessions.close_client_sessions()

        # logger.info("Received exit signal %s...", sig.name)
        #
        # tasks = [
        #     t for t in asyncio.all_tasks()
        #     if t is not asyncio.current_task()
        # ]
        #
        # [cancel_task(task) for task in tasks]
        #
        # logging.info("Canceling outstanding tasks")
        #
        # await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    for curr in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            curr, lambda s=curr: asyncio.create_task(shutdown(s)))
