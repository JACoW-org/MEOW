"""
Put Event
"""

# import anyio
# import logging
# 
# from typing import Any
# from meow.services.local.event.save_conference import put_conference_entity
# 
# from meow.tasks.infra.abstract_task import AbstractTask
# 
# logger = logging.getLogger(__name__)
# 
# 
# class EventPutTask(AbstractTask):
#     """ EventPutTask """
# 
#     async def run(self, params: dict) -> Any:
#         """ Main Function """
# 
#         conference_id: str = params.get("conference_id", "44")
#         
#         conference = await put_conference_entity(conference_id)
#         
#         return conference.dict()
