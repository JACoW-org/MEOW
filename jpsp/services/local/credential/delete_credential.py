import logging as lg

from redis.exceptions import RedisError

from jpsp.app.errors.service_error import ServiceError
from jpsp.models.application import Credential

logger = lg.getLogger(__name__)


async def del_all_credentials():
    """ """

    try:
        async with Credential.pipe() as pipe:

            Credential.delete(Credential.key('jpsp.indico.plugin.dev'), pipe)

            await pipe.execute()

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')
