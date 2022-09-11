from typing import Type
from jpsp.models.infra.base import BaseModel

from jpsp.models.application import Settings
from jpsp.models.conference import Conference, SessionSlot, Creator, Folder, Chair, Material, Resource, Attachment, \
    SessionSlotContribution, SessionEvent, SessionEventConvener, SessionSlotConvener, Author, CoAuthor, PrimaryAuthor, \
    Speaker

jpsp_settings: list[Type[BaseModel]] = [Settings]
    
jpsp_conference: list[Type[BaseModel]] = [Conference]

jpsp_conference_relates_entities: list[Type[BaseModel]] = [
    Creator,
    Folder,
    Chair,
    Material,
    Resource,
    Attachment,

    SessionSlot,
    SessionSlotContribution,
    SessionEvent,
    SessionEventConvener,
    SessionSlotConvener,

    Author,
    CoAuthor,
    PrimaryAuthor,
    Speaker
]

jpsp_conference_entities = jpsp_conference + jpsp_conference_relates_entities

jpsp_models = jpsp_settings + jpsp_conference_entities
