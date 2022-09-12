from lib2to3.pytree import Base
import logging as lg

from typing import Any

from jpsp.tasks.infra.task_factory import TaskFactory

from jpsp.app.instances.databases import dbs
from jpsp.utils.error import exception_to_string
from jpsp.utils.serialization import json_encode


logger = lg.getLogger(__name__)


class TaskRunner:
    """ """

    @classmethod
    async def run_task(cls, task_id: str, code: str, params: Any) -> Any:
        """ """

        try:

            args = dict(
                task_id=task_id
            )

            logger.debug(f"run_task {code} {args}")

            task_obj = await TaskFactory.create_task(code, args)

            logger.debug(f"run_task - task created")
            # logger.debug(f"run_task - task created {params}")
                        
            result = await task_obj.run(params)

            logger.debug(f"run_task - task result")
            # logger.debug(f"run_task - task result {result}")
            
            return result
        
        except BaseException as e:
            logger.error(e, exc_info=True)
            raise e
            
    
    @classmethod
    async def send_queued(cls, task_id: str, params: dict) -> None:   
        await cls.send('task:queued', dict(
            task_id=task_id,
            params=params
        ))
            
    
    @classmethod
    async def send_begin(cls, task_id: str, params: dict) -> None:   
        await cls.send('task:begin', dict(
            task_id=task_id,
            params=params
        ))
            
    
    @classmethod
    async def send_end(cls, task_id: str, result: dict) -> None:  
        await cls.send('task:end', dict(
            task_id=task_id,
            result=result
        ))
            
    
    @classmethod
    async def send_error(cls, task_id: str, error: BaseException) -> None:  
        await cls.send('task:error', dict(
            task_id=task_id,
            error=exception_to_string(error)
        ))
            
    
    @classmethod
    async def send(cls, event: str, body: dict) -> None:
        """ """
        
        try:
        
            logger.debug(f"send {event}")

            message = json_encode(
                dict(event=event, body=body)
            )

            await dbs.redis_client.publish("jpsp:feed", message)
            
        except BaseException as e:
            logger.error(e, exc_info=True)
