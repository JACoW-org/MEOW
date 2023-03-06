from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.track_model import TrackData
from meow.tasks.local.doi.models import ContributionDOI
from meow.tasks.local.reference.models import Reference


@dataclass(kw_only=True, slots=True)
class ContributionGroupKey:
    """ Contribution Group Key """

    session: str
    track: list[str]
    author: list[str]
    institute: list[str]
    doi_per_institute: list[str]
    keyword: list[str]

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class ContributionFieldData:
    """ Contribution Field """

    name: str
    value: str

    def as_dict(self) -> dict:
        return asdict(self)
    

@dataclass(kw_only=True, slots=True)
class FileData:
    """ File Data """
    
    content_type: str
    download_url: str
    external_download_url: str
    filename: str
    md5sum: str
    uuid: str
    
    
@dataclass(kw_only=True, slots=True)
class RevisionData:
    """ Revision Data """
    
    id: str
    files: list[FileData]
    comment: str

    def as_dict(self) -> dict:
        return asdict(self)
    

@dataclass(kw_only=True, slots=True)
class ContributionData:
    """ Contribution Data """

    code: str
    type: str
    url: str
    title: str
    description: str
    session_code: str

    start: datetime
    end: datetime
    
    reception: datetime
    acceptance: datetime
    issuance: datetime

    field_values: list[ContributionFieldData] = field(default_factory=list)
    
    speakers: list[PersonData] = field(default_factory=list)
    primary_authors: list[PersonData] = field(default_factory=list)
    coauthors: list[PersonData] = field(default_factory=list)
    
    revisions: list[RevisionData] = field(default_factory=list)
    
    keywords: list[KeywordData] = field(default_factory=list)
    authors: list[PersonData] = field(default_factory=list)
    institutes: list[AffiliationData] = field(default_factory=list)
    
    track: TrackData | None = field(default=None)
    
    editor: PersonData | None = field(default=None)
    duration: int | None = field(default=None)
    room: str | None = field(default=None)
    location: str | None = field(default=None)    
    
    page: int = field(default=None)
    metadata: dict | None = field(default=None)
    reference: Reference | None = field(default=None)    
    doi_data: ContributionDOI | None = field(default=None)    

    group_keys: ContributionGroupKey | None = field(default=None)

    def as_dict(self) -> dict:
        return asdict(self)
