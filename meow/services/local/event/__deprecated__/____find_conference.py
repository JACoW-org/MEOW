# import logging as lg
# from typing import Coroutine, Any
# 
# import anyio
# from redis.commands.search.query import Query
# from redis.exceptions import RedisError
# 
# from meow.app.errors.service_error import ServiceError
# from meow.models.conference import Chair, Material, Resource, Conference, Folder, Attachment, Creator, SessionEvent, \
#     SessionEventConvener, SessionSlotConvener, Speaker, PrimaryAuthor, Author, SessionSlotContribution, \
#     SessionSlot, CoAuthor
# 
# logger = lg.getLogger(__name__)
# 
# 
# async def get_conference_entity(conference_id: str) -> Conference | None:
#     """ """
# 
#     try:
# 
#         conference = await Conference.find_one(
#             Query(f"@id:({conference_id})")
#         )
# 
#         return conference
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
# async def get_conference_entities_ids(conference_id):
#     """ """
# 
#     def merge_results(results: list[list[Any]] | None, current: list[list[Any]]) -> list[list[Any]]:
#         return current if results is None else [
#             results[idx] + lst for idx, lst in enumerate(current)
#         ]
# 
#     async def task_wrapper(coro: Coroutine, index: int, results: list[list[Any]]):
#         results[index] = results[index] + (await coro)
# 
#     final_ids: list[list[Any]] | None = None
# 
#     try:
# 
#         stop_flag: bool = False
# 
#         paging_offset: int = 0
#         paging_limit: int = 500
# 
#         while not stop_flag:
# 
#             q = Query(f"@conference_id:{conference_id}") \
#                 .paging(paging_offset, paging_limit) \
#                 .sort_by('id') \
#                 .no_content()
# 
#             tasks: list[Coroutine] = [
#                 Creator.find_docs(q),
#                 Folder.find_docs(q),
#                 Chair.find_docs(q),
#                 Material.find_docs(q),
#                 Resource.find_docs(q),
#                 Attachment.find_docs(q),
#                 SessionEvent.find_docs(q),
#                 SessionEventConvener.find_docs(q),
#                 SessionSlotConvener.find_docs(q),
#                 SessionSlotContribution.find_docs(q),
#                 SessionSlot.find_docs(q),
#                 Author.find_docs(q),
#                 CoAuthor.find_docs(q),
#                 PrimaryAuthor.find_docs(q),
#                 Speaker.find_docs(q),
#             ]
# 
#             entities_ids: list[list[Any]] = [
#                 [] for _ in tasks
#             ]
# 
#             async with anyio.create_task_group() as tg:
#                 [
#                     tg.start_soon(task_wrapper, task, index, entities_ids)
#                     for index, task in enumerate(tasks)
#                 ]
# 
#             entities_count = sum(len(el) for el in entities_ids) if entities_ids else 0
# 
#             logger.info(f"entities_count --> {entities_count}")
#             # logger.info(f"entities_ids --> {entities_ids}")
# 
#             if entities_count > 0:
#                 final_ids = merge_results(final_ids, entities_ids)
#                 paging_offset = paging_offset + paging_limit
#             else:
#                 stop_flag = True
# 
#         final_count = sum(len(el) for el in final_ids) if final_ids else 0
# 
#         logger.info(f"final_count --> {final_count}")
#         # logger.info(f"final_ids --> {final_ids}")
# 
#         return final_ids
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
# async def get_conference_session_slots_entities(conference_id: str) -> list[SessionSlot] | None:
#     """ """
# 
#     try:
# 
#         session_slots = await SessionSlot.find_all(
#             Query(f"@conference_id:({conference_id})")
#             .sort_by('start_date')
#         )
# 
#         return session_slots
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
# async def get_conference_session_event_entity(conference_id: str,
#                                               session_slot_id: str) -> SessionEvent | None:
#     """ """
# 
#     try:
#         session_event = await SessionEvent.find_one(
#             Query(f"@session_slot_id:({session_slot_id})")
#         )
# 
#         return session_event
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
# async def get_conference_session_slots_conveners_entities(conference_id: str,
#                                                           session_slot_id: str) -> \
#         list[SessionSlotConvener] | None:
#     """ """
# 
#     try:
#         session_slot_conveners = await SessionSlotConvener.find_all(
#             Query(f"@session_slot_id:({session_slot_id})")
#         )
# 
#         return session_slot_conveners
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
# async def get_conference_session_slot_contribution_entities(conference_id: str,
#                                                             session_slot_id: str) -> \
#         list[SessionSlotContribution] | None:
#     """ """
# 
#     try:
#         session_slot_contributions = await SessionSlotContribution.find_all(
#             Query(f"@session_slot_id:({session_slot_id})")
#             .sort_by('start_date')
#         )
# 
#         return session_slot_contributions
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
# async def get_conference_session_slot_contribution_speakers_entities(conference_id: str,
#                                                                      session_slot_id: str,
#                                                                      contribution_id: str) -> list[Speaker] | None:
#     """ """
# 
#     try:
#         speakers = await Speaker.find_all(
#             Query(f"@contribution_id:({contribution_id})")
#         )
# 
#         return speakers
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
# async def get_conference_session_slot_contribution_primary_authors_entities(conference_id: str,
#                                                                             session_slot_id: str,
#                                                                             contribution_id: str) \
#         -> list[PrimaryAuthor] | None:
#     """ """
# 
#     try:
#         primary_authors = await PrimaryAuthor.find_all(
#             Query(f"@contribution_id:({contribution_id})")
#         )
# 
#         return primary_authors
# 
#     except RedisError as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Database error')
# 
#     except Exception as e:
#         logger.error(e, exc_info=True)
#         raise ServiceError('Generic error')
