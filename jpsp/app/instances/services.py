
from dataclasses import dataclass

from jpsp.services.infra.migrator import RedisSchemaMigrator

from jpsp.app.worker import RedisWorkerManager
from jpsp.app.socket import WebSocketManager

from jpsp.app.workers.pubsub import PubsubRedisWorkerLogicComponent

   

@dataclass
class __Instances:
    """ """
    
    redis_migrator = RedisSchemaMigrator()
       
    workers_manager = RedisWorkerManager(
        PubsubRedisWorkerLogicComponent()
    )
    
    ws_manager = WebSocketManager()
    


srs = __Instances()
