from dataclasses import dataclass
from enum import Enum
from io import StringIO

class ConferenceStatus(Enum):
    IN_PROCEEDINGS = '@inproceedings'
    CONFERENCE = '@conference'
    UNPUBLISHED = '@unpublished'

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
    reference: Reference

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


        first_last_name = None
        if len(self.reference.authors) > 0:
            first_last_name = self.reference.authors[0].get('last_name').lower()

        authors = ''
        for index, author in enumerate(self.reference.authors):
            if index > 0:
                authors += ' and '
            first_name = author.get('first_name')
            last_name = author.get('last_name')
            authors += f'{first_name[0].upper()}. {last_name}'

        stream = StringIO()
        
        stream.write(self.conference.status.value + '{')

        stream.write(f'{first_last_name}:{self.conference.code.lower()}-{self.reference.paper_id.lower()},\n')

        stream.write(f'\tauthor = {{{authors}}}\n')
        stream.write(f'\ttitle = {{{self.reference.title}}},\n')

        if self.conference.status is ConferenceStatus.IN_PROCEEDINGS:
            stream.write(f'\tbooktitle = {{{ self.reference.book_title }}}\n')

        stream.write(f'\tpages = {{{self.reference.pages if self.reference.pages is not None else ""}}}\n')

        stream.write(f'\tpaper = {{{self.reference.paper_id}}},\n')

        stream.write(f'\tvenue = {{{self.build_venue()}}},\n')

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

        first_last_name = None
        if len(self.reference.authors) > 0:
            first_last_name = self.reference.authors[0].get('last_name').lower()

        authors = ''
        for index, author in enumerate(self.reference.authors):
            if index > 0:
                authors += ' and '
            first_name = author.get('first_name')
            last_name = author.get('last_name')
            authors += f'{first_name[0].upper()}. {last_name}'

        return f"""
            %cite{{{first_last_name}}}:{self.conference.code}-{self.reference.paper_id}
            \\bibitem{{{first_last_name}}}:{self.conference.code}-{self.reference.paper_id}
            {authors},
            \\textquotedblleft{{{self.reference.title}}}\\textquotedblright,
            in \\emph{{{self.reference.book_title}}}, {self.conference.venue}, {self.reference.pages}
            \\url{{{self.reference.url}}}
        """

    def to_word(self) -> str:
        return ""
    
    def to_ris(self) -> str:
        return ""
    
    def to_xml(self) -> str:
        return ""

    def build_venue(self)-> str:
        if self.conference.year is None or self.conference.month is None:
            return self.conference.venue
        else:

            from calendar import month_abbr

            return f'{self.conference.venue}, {month_abbr[self.conference.month]} {self.conference.year}'
        