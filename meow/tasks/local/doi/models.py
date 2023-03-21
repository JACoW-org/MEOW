from dataclasses import dataclass, field, asdict
from typing import Optional
from meow.tasks.local.reference.models import Reference

@dataclass
class AuthorsGroup:
    affiliation: str = field(default='')
    authors: list[str] = field(default_factory=list)

@dataclass
class AuthorDOI:
    first_name: str = field(default='')
    last_name: str = field(default='')
    affiliation: str = field(default='')

@dataclass
class EditorDOI:
    first_name: str = field(default='')
    last_name: str = field(default='')
    affiliation: str = field(default='')

    def format(self):
        return f'{self.first_name} {self.last_name} ({self.affiliation})'

@dataclass
class ContributionDOI:
    ''''''

    code: str = field(default='')
    title: str = field(default='')
    # primary_authors: list[AuthorDOI] = field(default_factory=list[AuthorDOI])
    authors_groups: list[AuthorsGroup] = field(default_factory=list)
    abstract: str = field(default='')
    references: list = field(default_factory=list)
    paper_url: str = field(default='')
    slides_url: str = field(default='')
    reference: Optional[Reference] = field(default=None)  #  BibTeX, LaTeX, Text/Word, RIS, EndNote
    conference_code: str = field(default='')
    series: str = field(default='')
    venue: str = field(default='')
    start_date: str = field(default='')
    end_date: str = field(default='')
    date: str = field(default='')
    publisher: str = field(default='JaCoW Publishing')
    publisher_venue: str = field(default='Geneva, Switzerland')
    editors: list = field(default_factory=list) # TODO check Volker SCHEMA: first_name, last_name (affiliation)
    isbn: str = field(default='')
    issn: str = field(default='')
    reception_date: str = field(default='')
    # TODO missing revision date
    acceptance_date: str = field(default='')
    issuance_date: str = field(default='')
    doi_url: str = field(default='')
    start_page: str = field(default='')
    end_page: str = field(default='')
    pages: str = field(default='')

    def as_dict(self) -> dict:
        return asdict(self)
