from dataclasses import dataclass, asdict
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import PersonData

@dataclass(kw_only=True, slots=True)
class SessionData:
    """ Session Data """

    code: str
    title: str
    url: str
    is_poster: bool
    
    start: datetime
    end: datetime
    
    conveners: list[PersonData]
    
    room: str | None = None
    location: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)
