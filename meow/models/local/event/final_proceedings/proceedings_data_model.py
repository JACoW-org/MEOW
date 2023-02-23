from dataclasses import dataclass, asdict
from datetime import datetime
from meow.models.local.event.final_proceedings.contribution_model import ContributionData

from meow.models.local.event.final_proceedings.event_model import EventData
from meow.models.local.event.final_proceedings.session_model import SessionData

@dataclass
class ProceedingsData:
    """ """

    event: EventData
    sessions: list[SessionData]
    contributions: list[ContributionData]
    
    def as_dict(self) -> dict:
        return asdict(self)
    
