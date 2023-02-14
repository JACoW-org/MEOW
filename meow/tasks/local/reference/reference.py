from dataclasses import dataclass, asdict
from enum import Enum
from io import StringIO

class ConferenceStatus(Enum):
    # IN_PROCEEDINGS = '@inproceedings'
    # CONFERENCE = '@conference'
    # UNPUBLISHED = '@unpublished'
    IN_PROCEEDINGS = 'in_proceedings'
    CONFERENCE = 'conference'
    UNPUBLISHED = 'unpublished'

@dataclass
class Contribution:
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

@dataclass
class Conference:
    status: ConferenceStatus
    code: str
    series: str = None
    series_number: int = None
    month: int = None
    year: int = None
    venue: str = None
    issn: str = None
    isbn: str = None

@dataclass
class Reference:
    paper_id: str
    authors: list[str]
    title: str
    book_title: str = None
    pages: str = None
    url: str = None
    doi_verified: bool = None
    doi: str = None

@dataclass
class Citation:

    conference: Conference
    reference: Contribution

    publisher: str = 'JaCoW Publishing, Geneva, Switzerland'
    language: str = 'english'

    def is_citable(self) -> bool:
        return self.reference.authors is not None and len(self.reference.authors) > 0

    '''
    TODO:
    - @inproceedings if reference.conference.isPublished and reference.inProc (conferenza terminata e nella fase di generazione dei proceedings)
        elif @conference current_conference.hasCurrent and current_conference.current equals reference.conference (conferenza non pubblicata e contribution appartiene a tale conferenza)
        else @unpublished
    - author sempre presente
    - booktitle = reference.conference.code if reference.conference.isPublished (cioè quando ref ha tag @inproceedings)
    - pages = reference.position if reference.position and reference.position != 99-98 and reference.position != na
    - paper = reference.paperId
    - venue = 'reference.conference.location, reference.conference.year' if reference.conference.pubYear id null and reference.conference.pubMonth is null
    - intype = cablato, sempre 'presented at the' if reference.conference.isPublished and !reference.inProc
    - series = reference.conference.series if reference.conference.series
    - number = reference.conference.seriesNumber if reference.conference.seriesNumber
    - month = reference.conference.pubMonth if reference.conference.pubMonth
    - year = reference.conference.year if reference.conference.year
    - issn = reference.conference.issnFormatted if reference.conference.issn
    - isbn = reference.conference.isbnFormatted if reference.conference.isbn
    - doi = reference.doiOnly if reference.doiVerified
    - url = reference.paperUrl
    - note = 'presented at ' reference.conference.code, reference.conference.location, reference.conference.year, 'paper ' reference.paperId, if @conference then 'this conference' else 'unpublished',
    - language = 'english' sempre
    '''

    def to_bibtex(self) -> str:


        first_last_name = self._build_first_last_name()

        authors = self._build_authors()

        stream = StringIO()
        
        stream.write(self.conference.status.value + '{')

        stream.write(f'{first_last_name}:{self.conference.code.lower()}-{self.reference.paper_id.lower()},\n')

        stream.write(f'\tauthor = {{{authors}}}\n')
        stream.write(f'\ttitle = {{{self.reference.title}}},\n')

        if self.conference.status is ConferenceStatus.IN_PROCEEDINGS:
            stream.write(f'\tbooktitle = {{{ self.reference.book_title }}}\n')

        stream.write(f'\tpages = {{{self.reference.pages if self.reference.pages is not None else ""}}}\n')

        stream.write(f'\tpaper = {{{self.reference.paper_id}}},\n')

        stream.write(f'\tvenue = {{{self._build_venue()}}},\n')

        if self.conference.status is not ConferenceStatus.IN_PROCEEDINGS:
            stream.write('\tintype = {presented at the},\n')

        if self.conference.series is not None:
            stream.write(f'\tseries = {{{self.conference.series}}},\n')

        if self.conference.series_number is not None:
            stream.write(f'\tnumber = {{{self.conference.series_number}}},\n')

        stream.write(f'\tpublisher = {{{self.publisher}}},\n')

        if self.conference.month is not None:
            stream.write(f'\tmonth = {{{self.conference.month}}},\n')

        if self.conference.year is not None:
            stream.write(f'\tyear = {{{self.conference.year}}},\n')

        if self.conference.issn is not None:
            stream.write(f'\tissn = {{{self.conference.issn}}},\n')   # TODO format

        if self.conference.isbn is not None:
            stream.write(f'\tisbn = {{{self.conference.isbn}}},\n')   # TODO format

        if self.reference.doi_verified:
            stream.write(f'\tdoi = {{{self.reference.doi}}},\n')      # TODO review once doi is available

        stream.write(f'\turl = {{{self.reference.url}}},\n')

        if self.conference.status is not ConferenceStatus.IN_PROCEEDINGS:
            stream.write(f'\tnote = {{presented at {self.conference.code}, {self.conference.venue}, {self.conference.year}, paper {self.reference.paper_id}, unpublished}}\n')

        stream.write(f'\tlanguage = {{{self.language}}}\n')

        stream.write('}')

        return stream.getvalue()

    def to_latex(self) -> str:

        first_last_name = self._build_first_last_name()

        stream = StringIO()

        stream.write(f'%\cite{{{first_last_name}:{self.conference.code.upper()}-{self.reference.paper_id.upper()}}}\n')
        stream.write(f'\\bibitem{{{first_last_name}:{self.conference.code.upper()}-{self.reference.paper_id.upper()}}}\n')

        first_author = self.reference.authors[0]
        stream.write(f'\t{self._format_author(first_author.get("first_name"), first_author.get("last_name"))}')
        
        if len(self.reference.authors) > 1:
            stream.write(' \\emph{et al.}\n')
        else:
            stream.write('\n')

        stream.write(f'\t\\textquotedblleft{{{self.reference.title}}}\\textquotedblright\n')

        if self.conference.status is ConferenceStatus.IN_PROCEEDINGS:
            stream.write(f'\tin emph{{Proc. {self.reference.book_title}}}')
        else:
            stream.write(f'\tpresented at the {self.conference.code}')

        stream.write(f', {self._build_venue()}')
        
        if self.reference.pages is not None:
            stream.write(f', pp. {self.reference.pages}')

        if self.conference.status is ConferenceStatus.CONFERENCE:
            stream.write(f', this conference.')
        elif self.conference.status is ConferenceStatus.UNPUBLISHED:
            stream.write(f', unpublished.')

        if self.reference.doi_verified and self.reference.doi is not None:
            stream.write(f'\n\\url{{{self.reference.doi}}}')

        return stream.getvalue()

    def to_word(self) -> str:
        return ""
    
    def to_ris(self) -> str:
        return ""
    
    def to_xml(self) -> str:
        return ""

    def _build_first_last_name(self) -> str:

        first_last_name = self.reference.authors[0].get('last_name').lower()

        return first_last_name

    def _build_authors(self) -> str:
        authors = ''
        for index, author in enumerate(self.reference.authors):
            if index > 0:
                authors += ' and '
            first_name = author.get('first_name')
            last_name = author.get('last_name')
            authors += f'{first_name[0].upper()}. {last_name}'

        return authors

    def _format_author(self, first_name: str, last_name: str) -> str:
        author = f'{first_name[0].upper()}. {last_name}'

        return author

    def _build_venue(self)-> str:
        if self.conference.year is None or self.conference.month is None:
            return self.conference.venue
        else:

            from calendar import month_abbr

            return f'{self.conference.venue}, {month_abbr[self.conference.month]} {self.conference.year}'
        