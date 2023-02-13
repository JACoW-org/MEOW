# from typing import Type

from meow.models.application import Credential
from meow.models.infra.base import BaseModel

# from meow.models.conference import Conference, SessionSlot, Creator, Folder, Chair, Material, Resource, Attachment, \
#     SessionSlotContribution, SessionEvent, SessionEventConvener, SessionSlotConvener, Author, CoAuthor, PrimaryAuthor, \
#     Speaker
# 
#    
# meow_conference: list[Type[BaseModel]] = [Conference]
# 
# meow_conference_relates_entities: list[Type[BaseModel]] = [
#     Creator,
#     Folder,
#     Chair,
#     Material,
#     Resource,
#     Attachment,
# 
#     SessionSlot,
#     SessionSlotContribution,
#     SessionEvent,
#     SessionEventConvener,
#     SessionSlotConvener,
# 
#     Author,
#     CoAuthor,
#     PrimaryAuthor,
#     Speaker
# ]
# 
# meow_conference_entities = meow_conference + meow_conference_relates_entities

# meow_models = [Settings, Credential] + meow_conference_entities

meow_models: list[type[BaseModel]] = [Credential]
