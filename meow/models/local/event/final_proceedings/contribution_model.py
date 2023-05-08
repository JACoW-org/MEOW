from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.track_model import TrackData
from meow.tasks.local.doi.models import AuthorsGroup, ContributionDOI
from meow.tasks.local.reference.models import Reference


@dataclass(kw_only=True, slots=True)
class ContributionFieldData:
    """ Contribution Field """

    name: str
    value: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class TagData:
    """ Revision Tag """

    code: str
    color: str
    system: bool
    title: str
    
    @property
    def is_qa_approved(self):
        return self.title.lower() == "qa approved"
    
    @property
    def is_qa_pending(self):
        return self.title.lower() == "qa pending"
    
    @property
    def is_yellow(self):
        return self.color.lower() == "yellow"
    
    @property
    def is_green(self):
        return self.color.lower() == "green"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class FileData:
    """ File Data """

    file_type: int
    content_type: str
    download_url: str
    external_download_url: str
    filename: str
    md5sum: str
    uuid: str

    class FileType:
        # __titles__ = [None, _('Paper'), _('Slides'), _('Poster')]

        paper = 1
        slides = 2
        poster = 3


@dataclass(kw_only=True, slots=True)
class RevisionData:
    """ Revision Data """

    id: str
    files: list[FileData]
    tags: list[TagData]
    comment: str
    initial_state: int
    final_state: int

    creation_date: datetime
    
    @property
    def is_qa_approved(self) -> bool:
        if self.final_state == RevisionData.FinalRevisionState.accepted:
            return True
        
        for tag in self.tags:
            if tag.is_qa_approved:
                return True
        
        return False
    
    @property
    def is_qa_pending(self) -> bool:
        if self.is_qa_approved:
            return False
        
        if self.final_state == RevisionData.FinalRevisionState.needs_submitter_confirmation:
            return True
        
        for tag in self.tags:
            if tag.is_qa_pending:
                return True
            
        return False    

    def as_dict(self) -> dict:
        return asdict(self)

    class InitialRevisionState:
        # __titles__ = [None, _('New'), _('Ready for Review'), _('Needs Confirmation')]

        #: A revision that has been submitted by the user but isn't exposed to editors yet
        new = 1
        #: A revision that can be reviewed by editors
        ready_for_review = 2
        #: A revision with changes the submitter needs to approve or reject
        needs_submitter_confirmation = 3

    class FinalRevisionState:
        # __titles__ = [None, _('Replaced'), _('Needs Confirmation'), _('Needs Changes'), _('Accepted'), _('Rejected'), _('Undone')]

        #: A revision that is awaiting some action
        none = 0
        #: A revision that has been replaced by its next revision
        replaced = 1
        #: A revision that requires the submitter to confirm the next revision
        needs_submitter_confirmation = 2
        #: A revision that requires the submitter to submit a new revision
        needs_submitter_changes = 3
        #: A revision that has been accepted (no followup revision)
        accepted = 4
        #: A revision that has been rejected (no followup revision)
        rejected = 5
        #: A revision that has been undone
        undone = 6


@dataclass(kw_only=True, slots=True)
class EditableData:
    """ Contribution Data """

    id: str
    type: int

    all_revisions: list[RevisionData] = field(default_factory=list)
    latest_revision: RevisionData | None = field(default=None)

    class EditableType:
        # __titles__ = [None, _('Paper'), _('Slides'), _('Poster')]

        paper = 1
        slides = 2
        poster = 3


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
    
    is_qa_approved: bool = field(default=False)
    is_qa_pending: bool = field(default=False)

    reception: datetime | None = field(default=None)
    revisitation: datetime | None = field(default=None)
    acceptance: datetime | None = field(default=None)
    issuance: datetime | None = field(default=None)

    field_values: list[ContributionFieldData] = field(default_factory=list)

    speakers: list[PersonData] = field(default_factory=list)
    primary_authors: list[PersonData] = field(default_factory=list)
    coauthors: list[PersonData] = field(default_factory=list)

    paper: EditableData | None = field(default=None)
    slides: EditableData | None = field(default=None)
    poster: EditableData | None = field(default=None)

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

    @property
    def authors_list(self) -> list[PersonData]:
        return self.primary_authors + self.coauthors

    @property
    def authors_groups(self) -> list[AuthorsGroup]:
        authors_groups: list[AuthorsGroup] = list()
        for author in self.primary_authors:
            is_new_author = True
            for group in authors_groups:
                if author.affiliation == group.affiliation:
                    group.authors.append(author.short)
                    is_new_author = False
                    break
            if is_new_author:
                authors_groups.append(AuthorsGroup(
                    affiliation=author.affiliation,
                    authors=[author.short]
                ))
        return authors_groups

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
        return "cat--purr_meow"

    @property
    def producer_meta(self) -> str:
        return ""

    @property
    def authors_ref(self) -> str:
        return ", ".join([a.short for a in self.primary_authors])

    @property
    def track_meta(self) -> str:
        return self.track.full_name if self.track else ""

    def as_dict(self) -> dict:
        return {
            **asdict(self),
            'authors_list': [g.as_dict() for g in self.authors_list],
            'authors_groups': [g.as_dict() for g in self.authors_groups],
            'has_paper': self.has_paper(),
            'has_slides': self.has_slides(),
            'has_poster': self.has_poster(),
            'paper_name': self.paper_name(),
            'slides_name': self.slides_name(),
            'poster_name': self.poster_name(),
        }

    def has_paper(self) -> bool:
        if self.paper and self.paper.latest_revision and self.paper.latest_revision.files:
            for file in self.paper.latest_revision.files:
                if file.file_type == FileData.FileType.paper:
                    return True
        return False

    def paper_name(self) -> str | None:
        if self.paper and self.paper.latest_revision and self.paper.latest_revision.files:
            for file in self.paper.latest_revision.files:
                if file.file_type == FileData.FileType.paper:
                    return file.filename
        return None

    def has_slides(self) -> bool:
        if self.slides and self.slides.latest_revision and self.slides.latest_revision.files:
            for file in self.slides.latest_revision.files:
                if file.file_type == FileData.FileType.slides:
                    return True
        return False

    def slides_name(self) -> str | None:
        if self.slides and self.slides.latest_revision and self.slides.latest_revision.files:
            for file in self.slides.latest_revision.files:
                if file.file_type == FileData.FileType.slides:
                    return file.filename
        return None

    def has_poster(self) -> bool:
        if self.poster and self.poster.latest_revision and self.poster.latest_revision.files:
            for file in self.poster.latest_revision.files:
                if file.file_type == FileData.FileType.poster:
                    return True
        return False

    def poster_name(self) -> str | None:
        if self.poster and self.poster.latest_revision and self.poster.latest_revision.files:
            for file in self.poster.latest_revision.files:
                if file.file_type == FileData.FileType.poster:
                    return file.filename
        return None


@dataclass(kw_only=True, slots=True)
class ContributionPaperData:
    """ File Data """

    contribution: ContributionData
    paper: FileData

    def as_dict(self) -> dict:
        return asdict(self)
