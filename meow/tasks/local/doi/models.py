from dataclasses import dataclass, field

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

    title: str = field(default='')
    primary_authors: list[AuthorDOI] = field(default_factory=list[AuthorDOI])
    abstract: str = field(default='')
    references: list = field(default_factory=list)
    paper_url: str = field(default='')
    slides_url: str = field(default='')
    reference: dict = field(default_factory=dict)  #  BibTeX, LaTeX, Text/Word, RIS, EndNote TODO usare enum?
    conference_code: str = field(default='')
    series: str = field(default='')
    venue: str = field(default='')
    start_date: str = field(default='')
    end_date: str = field(default='')
    publisher: str = field(default='JaCoW Publishing')
    publisher_venue: str = field(default='Geneva, Switzerland')
    editors: list = field(default_factory=list) # TODO check Volker SCHEMA: first_name, last_name (affiliation)
    isbn: str = field(default='')
    issn: str = field(default='')
    reception_date: str = field(default='')
    acceptance_date: str = field(default='')
    issuance_date: str = field(default='')
    doi: str = field(default='')
    start_page: str = field(default='')
    number_of_pages: int = field(default=0)