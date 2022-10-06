import logging as lg
import time 

from typing import Any

from jpsp.tasks.infra.task_factory import TaskFactory

from jpsp.app.instances.databases import dbs
from jpsp.utils.error import exception_to_string
from jpsp.utils.serialization import json_encode


logger = lg.getLogger(__name__)


class TaskRunner:
    """ """

    @classmethod
    async def run_task(cls, task_id: str, code: str, params: dict, context: dict) -> Any:
        """ """

        try:

            args = dict(
                task_id=task_id
            )

            # logger.debug(f"run_task {code} {args}")

            task_obj = await TaskFactory.create_task(code, args)

            # logger.debug(f"run_task - task created")
                        
            result = await task_obj.run(params, context)

            # logger.debug(f"run_task - task result")
            
            return result
        
        except BaseException as e:
            logger.error(e, exc_info=True)
            raise e
            
    
    @classmethod
    async def send_queued(cls, task_id: str, task: str) -> None:   
        await cls.send('task:queued', task_id, task, None)
            
    
    @classmethod
    async def send_begin(cls, task_id: str, task: str) -> None:   
        await cls.send('task:begin', task_id, task, None)
            
    
    @classmethod
    async def send_end(cls, task_id: str, task: str, result: dict) -> None:  
        await cls.send('task:end', task_id, task, result)
            
    
    @classmethod
    async def send_error(cls, task_id: str, task: str, error: BaseException) -> None:  
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
        
            # logger.debug(f"send {event}")

            message = json_encode({
                'head': {
                    'code': event,
                    'uuid': task_id,
                    'time': int(time.time())
                }, 
                'body': {
                    'method': task,
                    'params': params
                }
            })

            await dbs.redis_client.publish("jpsp:feed", message)
            
        except BaseException as e:
            logger.error(e, exc_info=True)
