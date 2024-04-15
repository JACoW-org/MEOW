import logging as lg

from redis.exceptions import LockError

from meow.app.config import conf
from meow.app.instances.databases import dbs

from meow.factory.schema.redis_schema_factory import (
    create_search_index_info, create_search_index_meta)
from meow.models.infra.base import BaseModel
from meow.models.infra.locks import RedisLock, RedisLockList
from meow.models.infra.schema import RedisIndexMeta
from meow.utils.http import HttpClientSessions

logger = lg.getLogger(__name__)


class RedisManager:
    """ """

    def __init__(self):
        self.models: list[type[BaseModel]] = []

    async def prepare(self):
        """ """

        try:
            logger.info('--> fill_model_meta: START')

            for cls in self.models:
                await fill_model_meta(cls)

            logger.info('--> fill_model_meta: STOP')
        except LockError as e:
            logger.error(e, exc_info=True)
        except BaseException as e:
            logger.error(e, exc_info=True)

    async def migrate(self):
        """ """

        try:
            async with acquire_global_lock() as lock:
                logger.info(f'--> migrate_model_schema: START - {lock.name}')

                for cls in self.models:
                    await migrate_model_schema(cls)

                logger.info(f'--> migrate_model_schema: STOP - {lock.name}')
        except LockError as e:
            logger.error(e, exc_info=True)
        except BaseException as e:
            logger.error(e, exc_info=True)

    async def destroy(self):
        """ """

        try:
            await HttpClientSessions.close_client_sessions()
            await RedisLockList.release_all_locks()
        except BaseException as e:
            logger.error(e, exc_info=True)
        finally:
            try:
                await dbs.redis_client.aclose()
            except BaseException as e:
                logger.error(e, exc_info=True)

    async def popola(self):
        """ """

        try:
            pass
        except LockError as e:
            logger.error(e, exc_info=True)
        except BaseException as e:
            logger.error(e, exc_info=True)


def acquire_global_lock() -> RedisLock:

    return RedisLock(
        redis=dbs.redis_client,
        name=conf.REDIS_GLOBAL_LOCK_KEY,
        timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
        sleep=0.1,
        blocking=False,
        blocking_timeout=None,
        thread_local=True,
    )


async def fill_model_meta(cls: type[BaseModel]) -> None:
    try:

        logger.debug('fill_model_meta >>>')

        create_search_index_info(cls.SearchIndex)

    except Exception as e:
        logger.exception(e)


async def migrate_model_schema(cls: type[BaseModel]) -> None:
    try:

        logger.debug('migrate_model_schema >>>')

        meta: RedisIndexMeta = create_search_index_meta(cls)
        hash_val: bytes | None = await dbs.redis_client.get(meta.hash_key)

        if hash_val and str(hash_val, 'utf-8') == meta.hash_val:
            logger.debug(f'migrate_model_schema >>> {cls} >>> exit')
            return

        if hash_val:
            logger.debug(f'migrate_model_schema >>> {cls} >>> drop')
            await cls.ft().dropindex()

        logger.debug(f'migrate_model_schema >>> {cls} >>> create')
        await cls.ft().create_index(
            fields=meta.redis_schema,
            definition=meta.redis_definition
        )

        await dbs.redis_client.set(meta.hash_key, meta.hash_val)

    except Exception as e:
        logger.exception(e)
