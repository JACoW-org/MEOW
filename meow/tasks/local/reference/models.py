from dataclasses import dataclass, asdict, field
from enum import Enum

from meow.models.local.event.final_proceedings.event_model import PersonData


@dataclass
class Reference:
    bibtex: str
    latex: str
    word: str
    ris: str
    endnote: str

    def as_dict(self) -> dict:
        return asdict(self)


class ReferenceStatus(Enum):
    IN_PROCEEDINGS = "in_proceedings"
    CONFERENCE = "conference"  # not handled!
    UNPUBLISHED = "unpublished"


@dataclass
class ContributionRef:
    """Model to build reference in different pattern."""

    # mandatory
    id: str
    code: str
    status: str
    conference_code: str
    venue: str
    start_date: str
    end_date: str
    paper_code: str
    authors_list: list[PersonData]
    title: str
    abstract: str
    url: str
    year: str
    month: str

    # optional
    publisher: str = field(default="JACoW Publishing")
    publisher_venue: str = field(default="Geneva, Switzerland")
    language: str = field(default="English")
    series: str = field(default="")
    series_number: str = field(default="")
    issn: str = field(default="")
    isbn: str = field(default="")
    booktitle_short: str = field(default="")
    booktitle_long: str = field(default="")
    start_page: int = field(default=0)
    number_of_pages: int = field(default=0)
    doi: str = field(default="")
    keywords: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        dict_obj = asdict(self)
        return dict_obj

    def as_ref(self) -> dict:
        return {
            "contributionId": self.id,
            "paperId": self.code,
            "inProc": self.status == ReferenceStatus.IN_PROCEEDINGS.value,
            "position": f"{self.start_page}-{self.start_page + self.number_of_pages}",
            "title": self.title,
            "authors": [
                {"first": a.first, "last": a.last, "affiliations": a.affiliations_str}
                for a in self.authors_list
            ],
            "paperUrl": f"https://jacow.org/{self.conference_code}/pdf/{self.code}.pdf",
        }

    def is_citable(self) -> bool:
        return self.authors_list and len(self.authors_list) > 0
