from dataclasses import dataclass, asdict, field
from enum import Enum

class ConferenceStatus(Enum):
    IN_PROCEEDINGS = 'in_proceedings'
    CONFERENCE = 'conference'
    UNPUBLISHED = 'unpublished'

@dataclass
class ContributionRef:
    '''Model to build reference in different pattern.'''
    # mandatory
    conference_status: str
    conference_code: str
    venue: str
    start_date: str
    end_date: str
    paper_code: str
    primary_authors: list
    title: str
    abstract: str
    url: str

    # optional
    publisher: str = field(default='JaCoW Publishing')
    publisher_venue: str = field(default='Geneva, Switzerland')
    language: str = field(default='english')
    series: str = field(default='')
    series_number: str = field(default='')
    issn: str = field(default='')
    isbn: str = field(default='')
    book_title: str = field(default='')
    start_page: str = field(default='')
    number_of_pages: int = field(default=0)
    doi: str = field(default='')

    def as_dict(self) -> dict:
        dict_obj = asdict(self)
        return dict_obj

    def is_citable(self) -> bool:
        return self.primary_authors is not None and len(self.primary_authors) > 0
