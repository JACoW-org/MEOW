from dataclasses import dataclass, asdict, field
from enum import Enum


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
    IN_PROCEEDINGS = 'in_proceedings'
    CONFERENCE = 'conference'   # not handled!
    UNPUBLISHED = 'unpublished'


@dataclass
class ContributionRef:
    '''Model to build reference in different pattern.'''

    # mandatory
    status: str
    conference_code: str
    venue: str
    start_date: str
    end_date: str
    paper_code: str
    authors_list: list
    title: str
    abstract: str
    url: str
    year: str
    month: str

    # optional
    publisher: str = field(default='JACoW Publishing')
    publisher_venue: str = field(default='Geneva, Switzerland')
    language: str = field(default='English')
    series: str = field(default='')
    series_number: str = field(default='')
    issn: str = field(default='')
    isbn: str = field(default='')
    booktitle_short: str = field(default='')
    booktitle_long: str = field(default='')
    start_page: int = field(default=0)
    number_of_pages: int = field(default=0)
    doi: str = field(default='')
    keywords: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        dict_obj = asdict(self)
        return dict_obj

    def is_citable(self) -> bool:
        return self.authors_list and len(self.authors_list) > 0
