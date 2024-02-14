import abc
from dataclasses import dataclass
import logging as lg

import redis.asyncio as ar

from redis.asyncio.client import Pipeline

from redis.commands.json import JSON
from redis.commands.json.path import Path

from redis.commands.search import Search
from redis.commands.search.query import Query

from meow.app.config import conf
from meow.models.infra.fields import IndexField
from meow.models.infra.locks import RedisLock
from meow.utils.serialization import json_decode

logger = lg.getLogger(__name__)


class BaseSearchIndex:
    """ """

    db: str
    name: str
    fields: list[IndexField]

    model_key: str
    index_key: str
    hash_key: str
    hash_val: str

    r: ar.Redis


@dataclass
class AbstractModel(abc.ABC):
    """ """

    id: str

    class SearchIndex(BaseSearchIndex):
        pass


@dataclass
class BaseModel(AbstractModel):
    """ """

    @classmethod
    def delete(cls, model_key: str, pipe: Pipeline):
        # logger.debug(f">> delete -> {cls.key(model_id)}")
        pipe.json().delete(model_key)

    @classmethod
    def save(cls, model: AbstractModel, pipe: Pipeline):
        pipe.json().set(cls.key(model.id), str(Path('.')), model.__dict__)

    @classmethod
    def key(cls, model_id: str):
        return f"{cls.si().model_key}:{model_id}"

    @classmethod
    def lock(cls, model_id: str):
        return RedisLock(
            redis=cls.si().r,
            name=f"{cls.key(model_id)}:lock",
            timeout=conf.REDIS_LOCK_TIMEOUT_SECONDS,
            sleep=0.1,
            blocking=False,
            blocking_timeout=None,
            thread_local=True,
        )

    @classmethod
    def si(cls):
        return cls.SearchIndex

    @classmethod
    def r(cls) -> JSON:
        return cls.si().r.json()

    @classmethod
    def pipe(cls, transaction: bool = True) -> Pipeline:
        return cls.si().r.pipeline(transaction=transaction)

    @classmethod
    async def search(cls, query: Query):
        return await cls.ft().search(query)  # type: ignore

    @classmethod
    async def find_one(cls, query: Query):
        result = await cls.search(query)
        if not result or len(result.docs) == 0:
            return None
        one = result.docs[0].json
        return cls(**json_decode(one))

    @classmethod
    async def find_all(cls, query: Query):
        result = await cls.search(query)
        # logger.debug(f"find_all {len(result.docs)}")
        return [cls(**json_decode(d.json)) for d in result.docs]

    @classmethod
    async def find_docs(cls, query: Query):
        result = await cls.search(query)
        # logger.debug(f"find_docs {len(result.docs)}")
        return result.docs

    @classmethod
    def ft(cls) -> Search:
        si = cls.si()
        idx = si.index_key
        return si.r.ft(idx)
