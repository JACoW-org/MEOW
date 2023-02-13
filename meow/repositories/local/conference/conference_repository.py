# import logging as lg
# from typing import Any
# 
# from redis.asyncio.lock import Lock
# from redis.asyncio.client import Pipeline
# 
# from meow.factory.models.conference_models_factory import create_conference, create_conference_creator, \
#     create_conference_folder, create_conference_folder_attachment, create_conference_chair, create_conference_material, \
#     create_conference_material_resource, create_conference_session_slot, create_conference_session_slot_contribution, \
#     create_conference_session_event, create_conference_session_slot_convener, create_conference_session_event_convener, \
#     create_conference_speaker, create_conference_author
# from meow.models.conference import Chair, Material, Resource, Conference, Folder, Attachment, Creator, SessionEvent, \
#     SessionEventConvener, SessionSlotConvener, Speaker, PrimaryAuthor, Author, SessionSlotContribution, \
#     SessionSlot, CoAuthor
# from meow.repositories.indico.conference_indico_repository import get_indico_conference_data
# from meow.services.local.event.find_conference import get_conference_entities_ids
# 
# logger = lg.getLogger(__name__)
# 
# 
# async def del_conference_entity_pipe(conference_id: str, lock: Lock, pipe: Pipeline):
#     """ """
# 
#     logger.info(f'--> del_conference_entity_pipe: {conference_id} - START - {lock.name}')
# 
#     try:
#         # get conference related entities ids
#         entities_ids = await get_conference_entities_ids(conference_id)
# 
#         entities_len = sum(len(el) for el in entities_ids) if entities_ids else 0
# 
#         if entities_ids is not None and not entities_len == 0:
#             logger.info(f"entities_len -> {entities_len} -> delete")
# 
#             [Creator.delete(doc.id, pipe) for doc in entities_ids[0]]
#             [Folder.delete(doc.id, pipe) for doc in entities_ids[1]]
#             [Chair.delete(doc.id, pipe) for doc in entities_ids[2]]
#             [Material.delete(doc.id, pipe) for doc in entities_ids[3]]
#             [Resource.delete(doc.id, pipe) for doc in entities_ids[4]]
#             [Attachment.delete(doc.id, pipe) for doc in entities_ids[5]]
#             [SessionEvent.delete(doc.id, pipe) for doc in entities_ids[6]]
#             [SessionEventConvener.delete(doc.id, pipe) for doc in entities_ids[7]]
#             [SessionSlotConvener.delete(doc.id, pipe) for doc in entities_ids[8]]
#             [SessionSlotContribution.delete(doc.id, pipe) for doc in entities_ids[9]]
#             [SessionSlot.delete(doc.id, pipe) for doc in entities_ids[10]]
#             [Author.delete(doc.id, pipe) for doc in entities_ids[11]]
#             [CoAuthor.delete(doc.id, pipe) for doc in entities_ids[12]]
#             [PrimaryAuthor.delete(doc.id, pipe) for doc in entities_ids[13]]
#             [Speaker.delete(doc.id, pipe) for doc in entities_ids[14]]
# 
#             Conference.delete(Conference.key(conference_id), pipe)
#     except Exception as e:
#         logger.error(e, exc_info=True)
# 
#     logger.info(f'--> del_conference_entity_pipe: {conference_id} - STOP - {lock.name}')
# 
# 
# async def put_conference_entity_pipe(conference_id: str, lock: Lock, pipe: Pipeline):
#     """ """
# 
#     logger.info(f'--> put_conference_entity_pipe: {conference_id} - START - {lock.name}')
# 
#     # await pipe.watch(watch_key)
# 
#     # download json from indico
#     conference_data: Any = await get_indico_conference_data(conference_id)
# 
#     # delete conference related entities
#     await del_conference_entity_pipe(conference_id, lock, pipe)
# 
#     conference = create_conference(conference_id, conference_data)
#     Conference.save(conference, pipe)
# 
#     creator = create_conference_creator(conference_id, conference_data['creator'])
#     Creator.save(creator, pipe)
# 
#     for folder_data in conference_data['folders']:
#         folder = create_conference_folder(conference_id, folder_data)
#         Folder.save(folder, pipe)
# 
#         for attachment_data in folder_data['attachments']:
#             attachment = create_conference_folder_attachment(conference_id, folder.id, attachment_data)
#             Attachment.save(attachment, pipe)
# 
#     for chair_data in conference_data['chairs']:
#         chair = create_conference_chair(conference_id, chair_data)
#         Chair.save(chair, pipe)
# 
#     for material_data in conference_data['material']:
#         material = create_conference_material(conference_id, material_data)
#         Material.save(material, pipe)
# 
#         for resource_data in material_data['resources']:
#             resource = create_conference_material_resource(conference_id, material.id, resource_data)
#             Resource.save(resource, pipe)
# 
#     for session_slot_data in conference_data['sessions']:
#         session_slot = create_conference_session_slot(conference_id, session_slot_data)
#         SessionSlot.save(session_slot, pipe)
# 
#         for session_slot_contribution_data in session_slot_data['contributions']:
#             session_slot_contribution = create_conference_session_slot_contribution(conference_id,
#                                                                                     session_slot.id,
#                                                                                     session_slot_contribution_data)
#             SessionSlotContribution.save(session_slot_contribution, pipe)
# 
#             for speaker_data in session_slot_contribution_data['speakers']:
#                 speaker = create_conference_speaker(conference_id,
#                                                     session_slot.id,
#                                                     session_slot_contribution.id,
#                                                     speaker_data)
#                 Speaker.save(speaker, pipe)
# 
#             for author_data in session_slot_contribution_data['primaryauthors']:
#                 author = create_conference_author(conference_id,
#                                                   session_slot.id,
#                                                   session_slot_contribution.id,
#                                                   author_data)
#                 Author.save(author, pipe)
# 
#         for session_slot_convener_data in session_slot_data['conveners']:
#             session_slot_convener = create_conference_session_slot_convener(conference_id, session_slot.id,
#                                                                             session_slot_convener_data)
#             SessionSlotConvener.save(session_slot_convener, pipe)
# 
#         session_event = create_conference_session_event(conference_id, session_slot.id,
#                                                         session_slot_data['session'])
#         SessionEvent.save(session_event, pipe)
# 
#         for session_event_folder_data in session_slot_data['session']['folders']:
#             pass
# 
#         for session_event_material_data in session_slot_data['session']['material']:
#             pass
# 
#         for session_event_convener_data in session_slot_data['session']['sessionConveners']:
#             session_event_convener = create_conference_session_event_convener(conference_id,
#                                                                               session_slot.id,
#                                                                               session_event.id,
#                                                                               session_event_convener_data)
#             SessionEventConvener.save(session_event_convener, pipe)
# 
#     logger.info(f'--> put_conference_entity_pipe: {conference_id} - STOP - {lock.name}')
#     return conference
