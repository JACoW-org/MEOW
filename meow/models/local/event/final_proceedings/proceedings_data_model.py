from dataclasses import dataclass, asdict, field

from meow.models.local.event.final_proceedings.contribution_model import ContributionData
from meow.models.local.event.final_proceedings.event_model import AffiliationData, EventData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.models.local.event.final_proceedings.track_model import TrackData


@dataclass(kw_only=True, slots=True)
class ProceedingsData:
    """ """

    event: EventData
    contributions: list[ContributionData] = field(default_factory=list)

    sessions: list[SessionData] = field(default_factory=list)
    classification: list[TrackData] = field(default_factory=list)
    author: list[PersonData] = field(default_factory=list)
    keyword: list[KeywordData] = field(default_factory=list)
    institute: list[AffiliationData] = field(default_factory=list)
    doi_per_institute: list[AffiliationData] = field(default_factory=list)
    
    proceedings_volume_size: int = field(default=0)
    proceedings_brief_size: int = field(default=0)

    def as_dict(self) -> dict:
        return asdict(self)
