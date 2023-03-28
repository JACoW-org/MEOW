from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.track_model import TrackData
from meow.tasks.local.doi.models import ContributionDOI
from meow.tasks.local.reference.models import Reference


# @dataclass(kw_only=True, slots=True)
# class ContributionGroupKey:
#     """ Contribution Group Key """
#
#     session: str
#     track: list[str]
#     author: list[str]
#     institute: list[str]
#     doi_per_institute: list[str]
#     keyword: list[str]
#
#     def as_dict(self) -> dict:
#         return asdict(self)


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

    file_type: str
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

    all_revisions: list[RevisionData] = field(default_factory=list)
    latest_revision: RevisionData | None = field(default=None)

    keywords: list[KeywordData] = field(default_factory=list)
    authors: list[PersonData] = field(default_factory=list)
    institutes: list[AffiliationData] = field(default_factory=list)

    track: TrackData | None = field(default=None)

    editor: PersonData | None = field(default=None)
    duration: int | None = field(default=None)
    room: str | None = field(default=None)
    location: str | None = field(default=None)

    page: int = field(default=0)
    metadata: dict | None = field(default=None)
    reference: Reference | None = field(default=None)
    doi_data: ContributionDOI | None = field(default=None)

    start_page: int = field(default=0)
    page_count: int = field(default=0)

    @property
    def authors_list(self) -> list[PersonData]:
        return self.primary_authors + self.coauthors
    
    @property
    def title_meta(self) -> str:
        return self.title

    @property
    def authors_meta(self) -> str:
        return ", ".join([a.short for a in self.authors_list])

    @property
    def keywords_meta(self) -> str:
        return ", ".join([a.name for a in self.keywords])

    @property
    def creator_meta(self) -> str:
        return ""

    @property
    def producer_meta(self) -> str:
        return ""
    
    @property
    def authors_ref(self) -> str:
        return ", ".join([a.short for a in self.primary_authors])

    @property
    def track_meta(self) -> str:
        return self.track.full_name if self.track else ""

    # group_keys: ContributionGroupKey | None = field(default=None)

    def as_dict(self) -> dict:
        return asdict(self)
    
    def has_paper(self) -> bool:
        if self.latest_revision and self.latest_revision.files:
            for file in self.latest_revision.files:
                if file.file_type == 'paper':
                    return True
        return False


@dataclass(kw_only=True, slots=True)
class ContributionPaperData:
    """ File Data """

    contribution: ContributionData
    paper: FileData

    def as_dict(self) -> dict:
        return asdict(self)
