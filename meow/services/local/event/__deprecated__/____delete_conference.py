# import logging as lg
# 
# from redis.exceptions import LockError
# from redis.exceptions import WatchError
# from pydantic.error_wrappers import ValidationError
# 
# from meow.app.errors.service_error import ServiceError
# from meow.models.conference import Conference
# from meow.repositories.local.conference.conference_repository import del_conference_entity_pipe
# 
# logger = lg.getLogger(__name__)
# 
# 
# async def del_conference_entity(conference_id: str):
#     """ """
# 
#     try:
# 
#         logger.info(f'del_conference_entity: {conference_id} - BEGIN')
# 
#         async with Conference.lock(conference_id) as lock:
# 
#             async with Conference.pipe() as pipe:
#                 # delete conference and all related entities
#                 await del_conference_entity_pipe(conference_id, lock, pipe)
# 
#                 # commit transaction
#                 await pipe.execute()
# 
#         logger.info(f'del_conference_entity: {conference_id} - END')
# 
#     except ValidationError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Unable to build conference entities')
# 
#     except LockError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Unable to acquire conference lock')
# 
#     except WatchError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Unable to validate conference version')
# 
#     except Exception as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Unable to delete conference')
