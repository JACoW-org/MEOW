from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime

from meow.models.local.event.final_proceedings.event_model import AffiliationData, KeywordData, PersonData
from meow.models.local.event.final_proceedings.track_model import TrackData
from meow.tasks.local.doi.models import AuthorsGroup, ContributionDOI
from meow.tasks.local.reference.models import Reference


@dataclass(kw_only=True, slots=True)
class ContributionFieldData:
    """ Contribution Field """

    name: str = field()
    value: str = field()

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class TagData:
    """ Tag Data """

    code: str = field()
    color: str = field()
    system: bool = field()
    title: str = field()

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

    file_type: int = field()
    content_type: str = field()
    download_url: str = field()
    external_download_url: str = field()
    filename: str = field()
    md5sum: str = field()
    uuid: str = field()

    class FileType:
        # __titles__ = [None, _('Paper'), _('Slides'), _('Poster')]

        paper = 1
        slides = 2
        poster = 3


@dataclass(kw_only=True, slots=True)
class UserData:
    """ User Data """

    id: str = field()
    first_name: str = field()
    last_name: str = field()
    affiliation: str = field()
    is_admin: bool = field()
    is_system: bool = field()


@dataclass(kw_only=True, slots=True)
class RevisionCommentData:
    """ Revision Comment Data """

    id: str = field()
    text: str = field()
    internal: bool = field()
    system: bool = field()
    created_dt: datetime = field()
    user: UserData | None = field()

    @property
    def is_qa_approved(self) -> bool:
        return self.text == "This revision has passed QA."


@dataclass(kw_only=True, slots=True)
class RevisionData:
    """ Revision Data """

    id: str = field()
    files: list[FileData] = field(default_factory=list)
    tags: list[TagData] = field(default_factory=list)
    comments: list[RevisionCommentData] = field(default_factory=list)
    initial_state: int = field()
    final_state: int = field()

    creation_date: datetime = field()

    @property
    def is_accepted(self) -> bool:
        if self.final_state == RevisionData.FinalRevisionState.accepted \
                or self.final_state == RevisionData.FinalRevisionState.changes_acceptance:
            return True

        return False

    @property
    def is_qa_approved(self) -> bool:
        for comment in self.comments:
            if comment.is_qa_approved:
                return True

        return False

    @property
    def qa_approved_date(self) -> datetime | None:
        for comment in self.comments:
            if comment.is_qa_approved:
                return comment.created_dt

        return None

        # for tag in self.tags:
        #     if tag.is_qa_approved:
        #         return True
        #
        # return False

    def as_dict(self) -> dict:
        return asdict(self)

    class FinalRevisionState:
        #: A submitter revision that hasn't been exposed to editors yet
        new = 1
        #: A submitter revision that can be reviewed by editors
        ready_for_review = 2
        #: An editor revision with changes the submitter needs to approve or reject
        needs_submitter_confirmation = 3
        #: A submitter revision that accepts the changes made by the editor
        changes_acceptance = 4
        #: A submitter revision that rejects the changes made by the editor
        changes_rejection = 5
        #: An editor revision that requires the submitter to submit a new revision
        needs_submitter_changes = 6
        #: An editor revision that accepts the editable
        accepted = 7
        #: An editor revision that rejects the editable
        rejected = 8
        #: A system revision that replaces the current revision
        replacement = 9
        #: A system revision that resets the state of the editable to "ready for review"
        reset = 10


@dataclass(kw_only=True, slots=True)
class EditableData:
    """ Editable Data """

    id: str = field()
    type: int = field()
    state: int = field()

    all_revisions: list[RevisionData] = field(default_factory=list)
    latest_revision: RevisionData | None = field(default=None)

    class EditableType:

        paper = 1
        slides = 2
        poster = 3

    class EditableState:

        new = 1
        ready_for_review = 2
        needs_submitter_confirmation = 3
        needs_submitter_changes = 4
        accepted = 5
        rejected = 6
        accepted_by_submitter = 7


@dataclass
class DuplicateContributionData:
    """Duplicate Contribution Data"""

    code: str = field()
    session_id: int = field()
    session_code: str = field()

    has_metadata: bool = field(default=False)
    doi_url: str = field(default='')
    doi_label: str = field(default='')
    doi_name: str = field(default='')
    doi_path: str = field(default='')
    doi_identifier: str = field(default='')
    reception: datetime | None = field(default=None)
    revisitation: datetime | None = field(default=None)
    acceptance: datetime | None = field(default=None)
    issuance: datetime | None = field(default=None)

    def as_dict(self):
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class ContributionData:
    """ Contribution Data """

    code: str = field()
    type: str = field()
    url: str = field()
    title: str = field()
    description: str = field()
    session_id: int = field()
    session_code: str = field()

    start: datetime = field()
    end: datetime = field()

    is_slides_included: bool = field(default=False)
    is_included_in_pdf_check: bool = field(default=False)
    is_included_in_proceedings: bool = field(default=False)
    is_included_in_prepress: bool = field(default=False)

    peer_reviewing_accepted: bool = field(default=False)

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

    editors: list[PersonData] = field(default_factory=list)
    duration: int | None = field(default=None)
    room: str | None = field(default=None)
    location: str | None = field(default=None)

    page: int = field(default=0)
    page_count: int = field(default=0)
    paper_size: int = field(default=0)
    metadata: dict | None = field(default=None)
    reference: Reference | None = field(default=None)
    doi_data: ContributionDOI | None = field(default=None)

    duplicate_of: DuplicateContributionData | None = field(default=None)

    @property
    def authors_list(self) -> list[PersonData]:
        return self.primary_authors + self.coauthors

    @property
    def authors_groups(self) -> list[AuthorsGroup]:

        # subclass of dict that inits element with an empty list
        authors_groups_dict = defaultdict(list)

        for author in self.authors_list:
            authors_groups_dict[frozenset(author.affiliations)].append(author.short)
        
        authors_groups = [
            AuthorsGroup(affiliations=list(affiliations), authors=authors)
            for affiliations, authors in authors_groups_dict.items()
        ]

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
        return "Journals of Accelerator Conferences Website (JACoW)"

    @property
    def creator_tool_meta(self) -> str:
        return "JACoW Conference Assembly Tool (CAT)"

    @property
    def producer_meta(self) -> str:
        return "JACoW Conference Assembly Tool (CAT)"

    @property
    def authors_ref(self) -> str:
        return ", ".join([a.short for a in self.primary_authors])

    @property
    def track_meta(self) -> str:
        return self.track.full_name if self.track else ""

    def cat_publish(self, cat_publish_alias: str) -> bool:
        field_value: str = ''

        for _field in self.field_values:
            if _field.name == cat_publish_alias and _field.value:
                field_value = _field.value.lower()
                break

        return field_value in ['', 'yes', 'true', '1']

    def duplicate_of_code(self, duplicate_of_alias: str) -> str | None:
        # after duplicate of is initialized, use this condition
        if self.duplicate_of:
            return self.duplicate_of.code

        for _field in self.field_values:
            if _field.name == duplicate_of_alias and _field.value:
                return _field.value

        return None

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
            'duplicate_of': self.duplicate_of.as_dict() if self.duplicate_of else None
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

    # def duplicate_of(self) -> str:
    #     for field in self.field_values:
    #         if field.name == "duplicate_of" and field.value:
    #             return field.value
    #     return None


@dataclass(kw_only=True, slots=True)
class ContributionPaperData:
    """ File Data """

    contribution: ContributionData
    paper: FileData

    def as_dict(self) -> dict:
        return asdict(self)
