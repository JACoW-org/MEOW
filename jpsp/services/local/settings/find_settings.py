import logging as lg

from redis.commands.json.path import Path
from redis.exceptions import RedisError

from jpsp.app.errors.service_error import ServiceError
from jpsp.models.application import Settings

logger = lg.getLogger(__name__)


async def get_local_settings() -> Settings:
    """ """

    try:
        data = await Settings.r().get(Settings.key('0'), Path('.'))

        settings = Settings(**data)

        return settings

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')
