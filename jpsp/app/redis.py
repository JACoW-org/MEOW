from lib2to3.pytree import Base
import logging as lg


from jpsp.app.instances.services import srs
from jpsp.app.instances.databases import dbs


logger = lg.getLogger(__name__)


# async def create_redis_migrator():
#     """ """
# 
#     logger.debug("create_redis_migrator >>>")
# 
#     await srs.redis_migrator.prepare()
#     await srs.redis_migrator.migrate()


# async def create_redis_pool():
#     """ """
# 
#     logger.debug("create_redis_pool >>>")
# 
# 
#     # encoding = "utf-8",
#     # decode_responses = True



# async def destroy_redis_pool():
#     """ """
# 
#     logger.debug("destroy_redis_pool >>>")
#     
#     await dbs.redis_client.close()
#     
#     # try:
#     #     await dbs.redis_client.close()
#     # except BaseException as e:
#     #     pass
