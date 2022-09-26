import logging as lg

from redis.exceptions import RedisError

from jpsp.app.errors.service_error import ServiceError
from jpsp.models.application import Credential
from jpsp.services.local.credential.delete_credential import del_all_credentials

logger = lg.getLogger(__name__)


async def create_default_credentials():
    """ """

    try:

        await del_all_credentials()
        await put_default_credentials()

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')


async def put_default_credentials():
    """ """

    try:

        async with Credential.pipe() as pipe:
            settings = Credential(
                id='jpsp.indico.plugin.dev',
                label='Secret for JPSP-NG-DEV Indico Plugin',
                secret='01GDWDBTHHJNZ0KAVKZ1YP320S'
            )

            Credential.save(settings, pipe)

            await pipe.execute()

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')
