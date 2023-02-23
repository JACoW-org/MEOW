from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class EventPersonData:
    """ """

    id: str
    first: str
    last: str
    affiliation: str
    email: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class EventData:
    """ """

    id: str
    url: str
    title: str
    description: str
    location: str
    address: str
    
    start: datetime
    end: datetime

    def as_dict(self) -> dict:
        return asdict(self)
