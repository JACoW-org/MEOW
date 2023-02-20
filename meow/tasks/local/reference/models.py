from dataclasses import dataclass, asdict
from enum import Enum

class ConferenceStatus(Enum):
    IN_PROCEEDINGS = 'in_proceedings'
    CONFERENCE = 'conference'
    UNPUBLISHED = 'unpublished'

@dataclass
class ContributionRef:
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
    publisher: str = 'JaCoW Publishing'
    publisher_venue: str = 'Geneva, Switzerland'
    language: str = 'english'
    series: str = ''
    series_number: str = ''
    issn: str = ''
    isbn: str = ''
    book_title: str = ''
    start_page: str = ''
    number_of_pages: int = 0
    doi: str = ''

    def as_dict(self) -> dict:
        dict_obj = asdict(self)
        return dict_obj

    def is_citable(self) -> bool:
        return self.primary_authors is not None and len(self.primary_authors) > 0
