from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import PersonData

@dataclass(kw_only=True, slots=True)
class SessionData:
    """ Session Data """

    id: int = field()
    code: str = field()
    title: str = field()
    url: str = field()
    is_poster: bool = field()
    
    start: datetime = field()
    end: datetime = field()
    
    conveners: list[PersonData] = field(default_factory=list)
    
    room: str | None = field(default=None)
    location: str | None = field(default=None)

    def as_dict(self) -> dict:
        return asdict(self)
