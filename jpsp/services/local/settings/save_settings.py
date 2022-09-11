import logging as lg

from redis.exceptions import RedisError

from jpsp.app.errors.service_error import ServiceError
from jpsp.models.application import Settings
from jpsp.services.local.settings.delete_settings import del_all_settings

logger = lg.getLogger(__name__)


async def create_default_settings():
    """ """

    try:

        await del_all_settings()
        await put_default_settings()

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')


async def put_default_settings():
    """ """

    try:

        async with Settings.pipe() as pipe:
            settings = Settings(
                indico_http_url='https://indico.jacow.org',
                indico_api_key='01GA8P9WCVQR5GZ4ND5R7GQ6JH'
            )

            Settings.save(settings, pipe)

            await pipe.execute()

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')
