# import abc
# from typing import Optional
# 
# import pydantic as pd
# 
# import jpsp.models.infra.base as m
# from jpsp.models.infra.fields import TextIndexField, NumericIndexField
# 
# 
# # Creator: {
# #     "_type": "Avatar",
# #     "_fossil": "conferenceChairMetadata",
# #     "first_name": "Christine",
# #     "last_name": "Petit-Jean-Genaz",
# #     "fullName": "Petit-Jean-Genaz, Christine",
# #     "id": "533",
# #     "affiliation": "European Organization for Nuclear Research",
# #     "emailHash": "e725acdb89920b798484a116548c5bba"
# # }
# 
# class Creator(m.BaseModel):
#     """ """
# 
#     id: str = pd.Field()
#     first_name: str = pd.Field()
#     last_name: str = pd.Field()
#     affiliation: str = pd.Field()
# 
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'conference_creator'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # Folder: {
# #     "_type": "folder",
# #     "id": 172,
# #     "title": "SPC",
# #     "description": "",
# #     "attachments": [],
# #     "default_folder": false,
# #     "is_protected": true
# # }
# 
# class Folder(m.BaseModel):
#     """ """
# 
#     # attachments: list[Attachment]
# 
#     id: str = pd.Field()
#     title: str = pd.Field()
#     description: str = pd.Field()
# 
#     default_folder: int = pd.Field()
#     is_protected: int = pd.Field()
# 
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'folder'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # Chair: {
# #     "_type": "ConferenceChair",
# #     "_fossil": "conferenceChairMetadata",
# #     "first_name": "Luca",
# #     "last_name": "Giannessi",
# #     "fullName": "Giannessi, Luca",
# #     "id": "6",
# #     "affiliation": "Elettra",
# #     "emailHash": "c5350c011f76a90ef163bde22a2ea215",
# #     "db_id": 6,
# #     "person_id": 448
# # }
# 
# class Chair(m.BaseModel):
#     """ """
# 
#     id: str = pd.Field()
#     first_name: str = pd.Field()
#     last_name: str = pd.Field()
#     affiliation: str = pd.Field()
# 
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'chair'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # Material: {
# #     "_type": "Material",
# #     "_fossil": "materialMetadata",
# #     "_deprecated": true,
# #     "title": "SPC",
# #     "id": "172",
# #     "resources": []
# # }
# 
# class Material(m.BaseModel):
#     """ """
# 
#     # resources: list[Resource]
# 
#     id: str = pd.Field()
#     title: str = pd.Field()
# 
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'material'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # Resource: {
# #     "_deprecated": true,
# #     "_type": "LocalFile",
# #     "_fossil": "localFileMetadata",
# #     "id": "557",
# #     "name": "FEL2022_contributed_oral_proposals.xlsx",
# #     "fileName": "FEL2022_contributed_oral_proposals.xlsx",
# #     "url": "https:\/\/indico.jacow.org\/event\/44\/attachments\/172\/557\/FEL2022_contributed_oral_proposals.xlsx"
# # }
# 
# class Resource(m.BaseModel):
#     """ """
# 
#     id: str = pd.Field()
#     name: str = pd.Field()
#     file_name: str = pd.Field()
#     url: str = pd.Field()
# 
#     material_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'resource'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.material_id",
#                 field_name="material_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # Attachment: {
# #     "_type": "attachment",
# #     "id": 558,
# #     "download_url": "https:\/\/indico.jacow.org\/event\/44\/attachments\/172\/558\/FEL2022_contributed_oral_proposals.pdf",
# #     "title": "FEL2022_contributed_oral_proposals.pdf",
# #     "description": "",
# #     "modified_dt": "2022-06-06T14:16:50.401277+00:00",
# #     "type": "file",
# #     "is_protected": true,
# #     "filename": "FEL2022_contributed_oral_proposals.pdf",
# #     "content_type": "application\/pdf",
# #     "size": 385602,
# #     "checksum": "fa3935f1a44871f034b004ecdd7c98c7"
# # }
# 
# class Attachment(m.BaseModel):
#     """ """
# 
#     id: str = pd.Field()
#     title: str = pd.Field()
#     description: str = pd.Field()
#     type: str = pd.Field()
# 
#     file_name: str = pd.Field()
#     download_url: str = pd.Field()
#     content_type: str = pd.Field()
#     checksum: str = pd.Field()
#     size: int = pd.Field()
# 
#     modified_date: int = pd.Field()
# 
#     folder_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'attachment'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.start_date",
#                 field_name="start_date",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.end_date",
#                 field_name="end_date",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.folder_id",
#                 field_name="folder_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # SessionEvent: {
# #     "folders": [],
# #     "startDate": {
# #         "date": "2022-08-22",
# #         "time": "17:30:00",
# #         "tz": "Europe\/Zurich"
# #     },
# #     "endDate": {
# #         "date": "2022-08-22",
# #         "time": "19:00:00",
# #         "tz": "Europe\/Zurich"
# #     },
# #     "_type": "Session",
# #     "sessionConveners": [],
# #     "title": "Tutorial 1: How to expand your research network and write a successful  project proposal",
# #     "color": "#92b6db",
# #     "textColor": "#03070f",
# #     "description": "",
# #     "material": [],
# #     "isPoster": false,
# #     "type": null,
# #     "url": "https:\/\/indico.jacow.org\/event\/44\/sessions\/104\/",
# #     "roomFullname": "Auditorium Generali",
# #     "location": "Trieste Convention Centre",
# #     "address": "viale Miramare, 24\/2\nTrieste - Italy",
# #     "_fossil": "sessionMinimal",
# #     "numSlots": 1,
# #     "id": "5",
# #     "db_id": 104,
# #     "friendly_id": 5,
# #     "room": "Auditorium Generali",
# #     "code": ""
# # }
# 
# class SessionEvent(m.BaseModel):
#     """ """
# 
#     # folders: list[Folder]
#     # material: list[Material]
#     # sessionConveners: list[SessionEventConvener]
# 
#     id: str = pd.Field()
# 
#     code: Optional[str] = pd.Field()
#     type: Optional[str] = pd.Field()
#     url: Optional[str] = pd.Field()
#     title: Optional[str] = pd.Field()
#     description: Optional[str] = pd.Field()
# 
#     color: Optional[str] = pd.Field()
#     text_color: Optional[str] = pd.Field()
#     num_slots: Optional[str] = pd.Field()
# 
#     room: Optional[str] = pd.Field()
#     location: Optional[str] = pd.Field()
#     address: Optional[str] = pd.Field()
# 
#     start_date: int = pd.Field()
#     end_date: int = pd.Field()
# 
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'session_event'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.start_date",
#                 field_name="start_date",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.end_date",
#                 field_name="end_date",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # AbstractConvener: {
# #     "fax": "",
# #     "familyName": "Blasetti",
# #     "firstName": "Cecilia",
# #     "name": "Blasetti, Cecilia",
# #     "last_name": "Blasetti",
# #     "first_name": "Cecilia",
# #     "title": "",
# #     "_type": "SlotChair",
# #     "affiliation": "Elettra-Sincrotrone Trieste S.C.p.A.",
# #     "_fossil": "conferenceParticipation",
# #     "fullName": "Blasetti, Cecilia",
# #     "id": 2195,
# #     "db_id": 15,
# #     "person_id": 2195,
# #     "emailHash": "645976b4ab6551b59e23d73c492886d9",
# #     "address": [
# #         ""
# #     ],
# #     "phone": [
# #         ""
# #     ],
# #     "email": [
# #         "cecilia.blasetti@elettra.eu"
# #     ]
# # }
# 
# class AbstractConvener(m.BaseModel, abc.ABC):
#     """ """
# 
#     id: str = pd.Field()
# 
#     title: str = pd.Field()
#     first_name: str = pd.Field()
#     last_name: str = pd.Field()
#     affiliation: str = pd.Field()
# 
#     address: list[str] = pd.Field()
#     phone: list[str] = pd.Field()
#     email: list[str] = pd.Field()
# 
# 
# class SessionEventConvener(AbstractConvener):
#     """ """
# 
#     session_event_id: str = pd.Field()
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'session_event_convener'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_event_id",
#                 field_name="session_event_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# class SessionSlotConvener(AbstractConvener):
#     """ """
# 
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'session_slot_convener'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # SessionSlotContribution: {
# #     "_type": "Contribution",
# #     "_fossil": "contributionMetadataWithSubContribs",
# #     "id": "257",
# #     "db_id": 585,
# #     "friendly_id": 257,
# #     "title": "Calls overview and best practices examples",
# #     "startDate": {
# #         "date": "2022-08-22",
# #         "time": "18:15:00",
# #         "tz": "Europe/Zurich"
# #     },
# #     "endDate": {
# #         "date": "2022-08-22",
# #         "time": "18:40:00",
# #         "tz": "Europe/Zurich"
# #     },
# #     "duration": 25,
# #     "roomFullname": "Auditorium Generali",
# #     "room": "Auditorium Generali",
# #     "note": {},
# #     "location": "Trieste Convention Centre",
# #     "type": "Invited Orals",
# #     "description": "Networking, access and project opportunities for FEL and Laser research in Europe",
# #     "folders": [],
# #     "url": "https://indico.jacow.org/event/44/contributions/585/",
# #     "material": [],
# #     "speakers": [],
# #     "primaryauthors": [],
# #     "coauthors": [],
# #     "keywords": [],
# #     "track": null,
# #     "session": "Tutorial 1: How to expand your research network and write a successful  project proposal",
# #     "references": [],
# #     "board_number": "",
# #     "code": "",
# #     "subContributions": []
# # }
# 
# class AbstractContribution(m.BaseModel, abc.ABC):
#     """ """
# 
#     # folders: list[Folder]
#     # material: list[Material]
#     # speakers: list[Speaker]
#     # primaryauthors: list[PrimaryAuthor]
# 
#     id: str = pd.Field()
# 
#     code: str = pd.Field()
#     type: str = pd.Field()
#     url: str = pd.Field()
# 
#     title: str = pd.Field()
#     duration: int = pd.Field()
#     description: str = pd.Field()
#     session: str = pd.Field()
# 
#     keywords: list[str] = pd.Field()
# 
#     room: Optional[str] = pd.Field()
#     location: Optional[str] = pd.Field()
#     address: Optional[str] = pd.Field()
# 
#     start_date: int = pd.Field()
#     end_date: int = pd.Field()
# 
# 
# class SessionSlotContribution(AbstractContribution):
#     """ """
# 
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'session_slot_contribution'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.start_date",
#                 field_name="start_date",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.end_date",
#                 field_name="end_date",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # ContributionParticipation: {
# #     "_type": "ContributionParticipation",
# #     "_fossil": "contributionParticipationMetadata",
# #     "first_name": "Marie-Emmanuelle",
# #     "last_name": "Couprie",
# #     "fullName": "Couprie, Marie-Emmanuelle",
# #     "id": "2388",
# #     "affiliation": "Synchrotron Soleil",
# #     "emailHash": "ab56bb64ca94b50d93d949cd85b3f44c",
# #     "db_id": 2388,
# #     "person_id": 1745,
# #     "email": "marie-emmanuelle.couprie@synchrotron-soleil.fr"
# # }
# 
# class ContributionParticipation(m.BaseModel, abc.ABC):
#     """ """
# 
#     id: str = pd.Field()
# 
#     first_name: str = pd.Field()
#     last_name: str = pd.Field()
# 
#     affiliation: Optional[str] = pd.Field()
#     email: Optional[str] = pd.Field()
# 
# 
# class Author(ContributionParticipation):
#     """ """
# 
#     contribution_id: str = pd.Field()
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'author'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.contribution_id",
#                 field_name="contribution_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# class CoAuthor(ContributionParticipation):
#     """ """
# 
#     contribution_id: str = pd.Field()
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'co_author'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.contribution_id",
#                 field_name="contribution_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# class PrimaryAuthor(ContributionParticipation):
#     """ """
# 
#     contribution_id: str = pd.Field()
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'primary_author'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.contribution_id",
#                 field_name="contribution_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# class Speaker(ContributionParticipation):
#     """ """
# 
#     contribution_id: str = pd.Field()
#     session_slot_id: str = pd.Field()
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'speaker'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.contribution_id",
#                 field_name="contribution_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.session_slot_id",
#                 field_name="session_slot_id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# # SessionSlot: {
# #     "id": 115,
# #     "title": "Tutorial 1: How to expand your research network and write a successful  project proposal",
# #     "description": "",
# #     "url": "https:\/\/indico.jacow.org\/event\/44\/sessions\/104\/",
# #     "startDate": {
# #         "date": "2022-08-22",
# #         "time": "17:30:00",
# #         "tz": "Europe\/Zurich"
# #     },
# #     "endDate": {
# #         "date": "2022-08-22",
# #         "time": "19:00:00",
# #         "tz": "Europe\/Zurich"
# #     },
# #     "session": {},
# #     "room": "Auditorium Generali",
# #     "roomFullname": "Auditorium Generali",
# #     "location": "Trieste Convention Centre",
# #     "inheritLoc": true,
# #     "inheritRoom": true,
# #     "slotTitle": "",
# #     "address": "viale Miramare, 24\/2\nTrieste - Italy",
# #     "code": "",
# #     "note": [],
# #     "conveners": [],
# #     "allowed": {
# #         "users": [],
# #         "groups": []
# #     }
# # }
# 
# class SessionSlot(m.BaseModel):
#     """ """
# 
#     # contributions: list[SessionSlotContribution]
#     # conveners: list[SessionSlotConvener]
#     # session: SessionEvent
# 
#     id: str = pd.Field()
# 
#     url: str = pd.Field()
#     code: str = pd.Field()
# 
#     title: str = pd.Field()
#     description: str = pd.Field()
# 
#     room: Optional[str] = pd.Field()
#     location: Optional[str] = pd.Field()
#     address: Optional[str] = pd.Field()
# 
#     start_date: int = pd.Field()
#     end_date: int = pd.Field()
# 
#     conference_id: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'session_slot'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.title",
#                 field_name="title",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.start_date",
#                 field_name="start_date",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.end_date",
#                 field_name="end_date",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.conference_id",
#                 field_name="conference_id",
#                 is_sortable=True
#             ),
#         ]
# 
# 
# class Conference(m.BaseModel):
#     """ """
# 
#     # sessions: list[SessionSlot]
#     # contributions: list[Contribution]
#     # references: list[str]
# 
#     # folders: list[Folder]
#     # chairs: list[Chair]
#     # material: list[Material]
# 
#     id: str = pd.Field()
#     url: str = pd.Field()
#     title: str = pd.Field()
#     description: str = pd.Field()
#     # note: list[str] = ar.Field(index=True, default=[])
# 
#     timezone: str = pd.Field()
#     start_date: int = pd.Field()
#     end_date: int = pd.Field()
#     creation_date: int = pd.Field()
# 
#     room: str = pd.Field()
#     location: str = pd.Field()
#     address: str = pd.Field()
# 
#     keywords: list[str] = pd.Field()
# 
#     organizer: str = pd.Field()
# 
#     class SearchIndex:
#         db = 'jpsp'
#         name = 'conference'
#         fields = [
#             TextIndexField(
#                 field_code="$.id",
#                 field_name="id",
#                 is_sortable=True
#             ),
#             TextIndexField(
#                 field_code="$.title",
#                 field_name="title",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.start_date",
#                 field_name="start_date",
#                 is_sortable=True
#             ),
#             NumericIndexField(
#                 field_code="$.end_date",
#                 field_name="end_date",
#                 is_sortable=True
#            ),
#        ]
