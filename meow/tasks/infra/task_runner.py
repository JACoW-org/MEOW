from asyncio.exceptions import CancelledError
import logging as lg
import time

from typing import AsyncGenerator

from meow.app.errors.service_error import ServiceError

from meow.tasks.infra.task_factory import TaskFactory

from meow.app.instances.databases import dbs
from meow.tasks.infra.task_status import TaskStatus

from meow.utils.error import exception_to_string
from meow.utils.serialization import json_encode


logger = lg.getLogger(__name__)


class TaskRunner:
    """ """

    @classmethod
    async def run_task(cls, task_id: str, code: str, params: dict, context: dict) -> AsyncGenerator:
        """ """

        try:

            # logger.debug(f"run_task {code} {args}")

            task_obj = await TaskFactory.create_task(code, task_id)

            # logger.debug(f"run_task - task created")

            TaskStatus.start_task(task_id=task_id)

            gen = task_obj.run(params, context)

            async for p in gen:  # type: ignore
                yield p

            # logger.debug(f"run_task - task result")

        except ServiceError:
            logger.error(f"Task killed {task_id}")
        except CancelledError:
            logger.error(f"Task cancelled {task_id}")
        except BaseException as be:
            logger.error(be, exc_info=True)
            raise be
        finally:
            TaskStatus.stop_task(task_id=task_id)

    @classmethod
    async def kill_task(cls, task_id: str) -> None:
        logger.debug(f"kill_task {task_id}")
        TaskStatus.stop_task(task_id=task_id)

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
    async def send(cls, event: str, task_id: str, task: str | None, params: dict | None) -> None:

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

            to_send = json_encode({
                'head': {
                    'code': event,
                    'uuid': task_id,
                    'time': int(time.time())
                },
                'body': {
                    'method': task,
                    'params': params
                } if task else None
            })

            # logger.debug(f"send {to_send}")

            await dbs.redis_client.publish("meow:feed", to_send)

        except CancelledError as ace:
            logger.debug(ace, exc_info=True)
            raise ace
        except BaseException as ex:
            logger.error(ex, exc_info=True)
            raise ex
