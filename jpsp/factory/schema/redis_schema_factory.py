from typing import Type

from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from jpsp.models.infra.base import BaseSearchIndex, BaseModel
from jpsp.models.infra.fields import IndexField
from jpsp.models.infra.schema import RedisIndexMeta
from jpsp.utils.hash import sha1sum_hash

from jpsp.app.instances.databases import dbs


def create_search_index_info(si: type[BaseSearchIndex]) -> Type[BaseSearchIndex]:
    """ """

    model_key: str = f"{si.db}:{si.name}"
    index_key: str = f"{model_key}:index"
    hash_key: str = f"{model_key}:hash"

    si.model_key = model_key
    si.index_key = index_key
    si.hash_key = hash_key

    si.r = dbs.redis_client

    return si


def create_search_index_meta(cls: type[BaseModel]) -> RedisIndexMeta:
    """ """

    if cls.SearchIndex:
        fields: list = cls.SearchIndex.fields

        model_key: str = cls.SearchIndex.model_key
        index_key: str = cls.SearchIndex.index_key
        hash_key: str = cls.SearchIndex.hash_key
        hash_val: str = create_search_index_hash(cls)
        redis_schema: list = [f.get_redis_field() for f in fields]

        redis_definition = IndexDefinition(
            prefix=[f"{model_key}:"],
            index_type=IndexType.JSON
        )

        return RedisIndexMeta(
            index_key=index_key,
            hash_key=hash_key,
            hash_val=hash_val,
            redis_schema=redis_schema,
            redis_definition=redis_definition
        )

    raise RuntimeError('Invalid search index class')


def create_search_index_hash(cls: type[BaseModel]) -> str:
    """  """

    if cls.SearchIndex:
        db: str = cls.SearchIndex.db
        name: str = cls.SearchIndex.name
        fields: list[IndexField] = cls.SearchIndex.fields

        return sha1sum_hash((
            db,
            name,
            fields
        ))

    raise RuntimeError('Invalid search index class')
