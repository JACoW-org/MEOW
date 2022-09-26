import logging as lg

from redis.commands.json.path import Path
from redis.exceptions import RedisError
from redis.commands.search.query import Query

from jpsp.app.errors.service_error import ServiceError
from jpsp.models.application import Credential

logger = lg.getLogger(__name__)


async def find_credential_by_secret(secret: str) -> Credential | None:
    """ """

    try:

        credential = await Credential.find_one(
            Query(f"@secret:({secret})")
        )

        return credential

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')



async def get_local_credential() -> Credential:
    """ """

    try:
        data = await Credential.r().get(Credential.key('jpsp.indico.plugin.dev'), Path('.'))

        settings = Credential(**data)

        return settings

    except RedisError as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Database error')

    except Exception as e:
        logger.error(e, exc_info=True)
        raise ServiceError('Generic error')
