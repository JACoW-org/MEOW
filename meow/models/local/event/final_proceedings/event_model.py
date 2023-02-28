from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass(kw_only=True, slots=True)
class PersonData:
    """ """

    id: str
    first: str
    last: str
    affiliation: str
    email: str
    
    @property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @property
    def full(self) -> str:
        return f"{self.first} {self.last} ({self.affiliation})"

    def __eq__(self, other):
        return self.first == other.first and \
            self.last == other.last and \
            self.affiliation == other.affiliation and \
            self.id == other.id

    def __hash__(self):
        return hash(('first', self.first,
                     'last', self.last,
                     'affiliation', self.affiliation,
                     'id', self.id))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class AffiliationData:

    id: str
    name: str
    street: str
    postcode: str
    city: str
    country_code: str

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class KeywordData:

    code: str
    name: str

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(('code', self.code))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
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

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id,
                     'title', self.title,
                     'url', self.url))

    def as_dict(self) -> dict:
        return asdict(self)
