from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional



@dataclass(kw_only=True, slots=True)
class TrackGroupData:
    """ Track Group Data """

    code: str
    title: str
    description: str
    
    @property
    def name(self) -> str:
        return f"{self.title}"

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(('code', self.code,
                     'title', self.title))

    def as_dict(self) -> dict:
        return asdict(self)



@dataclass(kw_only=True, slots=True)
class TrackData:
    """ Track Data """

    code: str
    title: str
    description: str
    
    track_group: TrackGroupData | None = None
    
    @property
    def name(self) -> str:
        return f"{self.title}"

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(('code', self.code,
                     'title', self.title))

    def as_dict(self) -> dict:
        return asdict(self)