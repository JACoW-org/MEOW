import logging as lg

from redis.exceptions import RedisError

from meow.app.errors.service_error import ServiceError
from meow.models.application import Credential
from meow.app.instances.databases import dbs


logger = lg.getLogger(__name__)


async def find_credential_by_secret(key: str | None) -> Credential | None:
    """ """

    try:

        if key is None:
            raise ServiceError('Invalid secret')

        res = await dbs.redis_client.hgetall(f'meow:credential:{key}')

        if res:

            user: bytes = res.get(b'user', None)
            host: bytes = res.get(b'host', None)
            date: bytes = res.get(b'date', None)

            print(user.decode('utf-8'), host.decode('utf-8'))

            return Credential(key=key,
                              user=user.decode('utf-8'),
                              host=host.decode('utf-8'),
                              date=date.decode('utf-8'))

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')

    return None
