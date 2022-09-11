
from pydantic.dataclasses import dataclass
from ulid import ULID

from os import environ

@dataclass
class __Config:
    """ """
    
    ADMIN_EMAIL: str = 'meneghetti.fabio@gmail.com'
    
    REDIS_SERVER_HOST: str = str(environ.get('REDIS_HOST', '127.0.0.1'))
    REDIS_SERVER_PORT: int = int(environ.get('REDIS_PORT', '6379'))
    REDIS_CLIENT_NAME: str = f'worker_{str(ULID())}'
    
    REDIS_NODE_TOPIC: str = REDIS_CLIENT_NAME
    
    REDIS_GLOBAL_LOCK_KEY: str = f"jpsp:global:lock"
    REDIS_LOCK_TIMEOUT_SECONDS: int = 3600  # 1 hour
    
    HTTP_REQUEST_TIMEOUT_SECONDS: int = 360  # 5 minutes
    


conf = __Config()
