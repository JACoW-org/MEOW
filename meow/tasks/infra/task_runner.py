import logging as lg
import time

from typing import Any, AsyncGenerator

from meow.tasks.infra.task_factory import TaskFactory

from meow.app.instances.databases import dbs
from meow.utils.error import exception_to_string
from meow.utils.serialization import json_encode


logger = lg.getLogger(__name__)


class TaskRunner:
    """ """

    @classmethod
    async def run_task(cls, task_id: str, code: str, params: dict, context: dict) -> AsyncGenerator:
        """ """

        try:

            args = dict(task_id=task_id)

            # logger.debug(f"run_task {code} {args}")

            task_obj = await TaskFactory.create_task(code, args)

            # logger.debug(f"run_task - task created")

            async for p in task_obj.run(params, context):  # type: ignore
                yield p

            # logger.debug(f"run_task - task result")

        except BaseException as e:
            logger.error(e, exc_info=True)
            raise e

    @classmethod
    async def send_queued(cls, task_id: str, task: str) -> None:
        logger.debug(f"send_queued {task_id} {task}")
        await cls.send('task:queued', task_id, task, None)

    @classmethod
    async def send_begin(cls, task_id: str, task: str) -> None:
        logger.debug(f"send_begin {task_id} {task}")
        await cls.send('task:begin', task_id, task, None)

    @classmethod
    async def send_progress(cls, task_id: str, task: str, progress: dict) -> None:
        logger.debug(f"send_progress {task_id} {task}")
        await cls.send('task:progress', task_id, task, progress)

    @classmethod
    async def send_log(cls, task_id: str, task: str, log: dict) -> None:
        logger.debug(f"send_log {task_id} {task}")
        await cls.send('task:log', task_id, task, log)

    @classmethod
    async def send_result(cls, task_id: str, task: str, result: dict) -> None:
        logger.debug(f"send_result {task_id} {task}")
        await cls.send('task:result', task_id, task, result)

    @classmethod
    async def send_end(cls, task_id: str, task: str, result: dict) -> None:
        logger.debug(f"send_end {task_id} {task}")
        await cls.send('task:end', task_id, task, result)

    @classmethod
    async def send_error(cls, task_id: str, task: str, error: BaseException) -> None:
        logger.debug(f"send_error {task_id} {task}")
        await cls.send('task:error', task_id, task, exception_to_string(error))

    @classmethod
    async def send(cls, event: str, task_id: str, task: str, params: dict | None) -> None:

        # head: {
        #     code: 'exec_task',
        #     uuid: ulid(),
        #     time: time
        # },
        # body: {
        #     method: 'event_ab',
        #     params: params
        # },

        """ """

        try:

            to_send = {
                'head': {
                    'code': event,
                    'uuid': task_id,
                    'time': int(time.time())
                },
                'body': {
                    'method': task,
                    'params': params
                }
            }

            logger.debug(f"send {to_send}")

            message = json_encode(to_send)

            await dbs.redis_client.publish("meow:feed", message)

        except BaseException as e:
            logger.error(e, exc_info=True)
