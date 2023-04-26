
from dataclasses import dataclass
from ulid import ULID

from os import environ


@dataclass
class __Config:
    """ """

    SERVER_PORT: int = int(environ.get('SERVER_PORT', '8080'))
    LOG_LEVEL: str = environ.get('LOG_LEVEL', 'info')

    ADMIN_EMAIL: str = 'meneghetti.fabio@gmail.com'

    CLIENT_TYPE: str = str(environ.get('CLIENT_TYPE'))

    REDIS_SERVER_HOST: str = str(environ.get('REDIS_HOST', '127.0.0.1'))
    REDIS_SERVER_PORT: int = int(environ.get('REDIS_PORT', '6379'))
    REDIS_CLIENT_NAME: str = f'{CLIENT_TYPE}_{str(ULID())}'

    REDIS_NODE_TOPIC: str = REDIS_CLIENT_NAME

    def REDIS_EVENT_LOCK_KEY(self, key: str) -> str:
        return f"meow:lock:event:{key}"

    REDIS_GLOBAL_LOCK_KEY: str = f"meow:lock:global"
    REDIS_LOCK_TIMEOUT_SECONDS: int = 3600  # 1 hour
    REDIS_LOCK_BLOCKING_TIMEOUT_SECONDS: int = 3600  # 1 hour

    HTTP_REQUEST_TIMEOUT_SECONDS: int = 360  # 5 minutes


conf = __Config()
