# import logging as lg
#
# from redis.exceptions import RedisError
#
# from meow.app.errors.service_error import ServiceError
# from meow.models.application import Credential
# from meow.services.local.credential.delete_credential import (
#     del_all_credentials)
#
# logger = lg.getLogger(__name__)
#
#
# async def create_default_credentials():
#     """ """
#
#     try:
#
#         await del_all_credentials()
#         await put_default_credentials()
#
#     except RedisError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Database error')
#
#     except Exception as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Generic error')
#
#
# async def put_default_credentials():
#     """ """
#
#     try:
#
#         async with Credential.pipe() as pipe:
#             settings = Credential(
#                 id='meow.indico.plugin.dev',
#                 label='Secret for PURR',
#                 secret='01GDWDBTHHJNZ0KAVKZ1YP320S'
#             )
#
#             Credential.save(settings, pipe)
#
#             await pipe.execute()
#
#     except RedisError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Database error')
#
#     except Exception as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Generic error')
#
