from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import PersonData

def session_page_name(session_id: int | str, code: str | None) -> str:
    """Name of the session page in the site: ``{id}-{code}``, or the id only
    for a session without a code (JACoW-org/MEOW#39)."""
    return f"{session_id}-{code.lower()}" if code else f"{session_id}"


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

    @property
    def page_name(self) -> str:
        return session_page_name(self.id, self.code)

    def as_dict(self) -> dict:
        return asdict(self)
