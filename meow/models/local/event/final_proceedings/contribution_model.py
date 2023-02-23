from dataclasses import dataclass, asdict
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import EventPersonData
from meow.tasks.local.doi.models import ContributionDOI
from meow.tasks.local.reference.models import Reference


@dataclass
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


@dataclass
class ContributionFieldData:
    """ Contribution Field """

    name: str
    value: str

    def as_dict(self) -> dict:
        return asdict(self)
    

@dataclass
class FileData:
    """ File Data """
    
    content_type: str
    download_url: str
    external_download_url: str
    filename: str
    md5sum: str
    uuid: str
    
    
@dataclass
class RevisionData:
    """ Revision Data """
    id: str
    files: list[FileData]
    comment: str

    def as_dict(self) -> dict:
        return asdict(self)
    

@dataclass
class ContributionData:
    """ Contribution Data """

    code: str
    type: str
    url: str
    title: str
    description: str
    session_code: str
    track: list[str]

    start: datetime
    end: datetime
    
    reception: datetime
    acceptance: datetime
    issuance: datetime

    field_values: list[ContributionFieldData]
    
    speakers: list[EventPersonData]
    primary_authors: list[EventPersonData]
    coauthors: list[EventPersonData]
    
    revisions: list[RevisionData]
    
    editor: EventPersonData | None = None    
    duration: int | None = None
    room: str | None = None
    location: str | None = None    
    
    metadata: dict | None = None
    reference: Reference | None = None    
    doi_data: ContributionDOI | None = None    

    group_keys: ContributionGroupKey | None = None

    def as_dict(self) -> dict:
        return asdict(self)
