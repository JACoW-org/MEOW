import asyncio
import logging

from typing import Callable, Any, Optional

from jpsp.app.workers.logic import AbsRedisWorkerLogicComponent

from jpsp.utils.task_exception import create_task, cancel_task



logger = logging.getLogger(__name__)


class RedisWorkerManager():
    """ """

    def __init__(self, logic: AbsRedisWorkerLogicComponent):

        self.logic: AbsRedisWorkerLogicComponent = logic
        self.task: Optional[asyncio.Task] = None
        self.queue: asyncio.Queue = asyncio.Queue(0)

    async def unsubscribe(self):
        logger.info(f"unsubscribe >>> worker_group: 'worker_group'")
        if self.task is not None:
            cancel_task(self.task, logger)
            self.task = None

    async def subscribe(self):
        if self.task is None:
            logger.info(f"subscribe >>> worker_group: 'worker_group'")

            async def on_message(data: Any):
                # logger.debug(f"__process data {data}")

                # message = deserialize(data)
                # logger.debug(f"__process message {message}")

                await self.queue.put("exec_process")

            __callable: Callable = await self.logic.subscribe(on_message=on_message)

            self.task = create_task(
                __callable(),
                name=f'worker_task',
                logger=self.logic.create_logger(),
                message=self.logic.exception_message()
            )

    async def publish(self, message: dict):
        await self.logic.publish(message)

