from dataclasses import dataclass
from enum import Enum
from io import StringIO

class ConferenceStatus(Enum):
    IN_PROCEEDINGS = '@inproceedings'
    CONFERENCE = '@conference'
    UNPUBLISHED = '@unpublished'

@dataclass
class Conference:
    conference_status: ConferenceStatus
    conference_code: str
    conference_series: str = None
    conference_series_number: int = None
    conference_pub_month: int = None
    conference_pub_year: int = None
    conference_issn: str = None
    conference_isbn: str = None

@dataclass
class Reference:
    paper_id: str
    authors: list[str]
    title: str
    book_title: str = None
    pages: str = None
    paper: str = None
    venue: str = None
    url: str = None
    doi_verified: bool = None
    doi: str = None

@dataclass
class Citation:

    conference: Conference
    reference: Reference

    publisher: str = 'JaCoW Publishing, Geneva, Switzerland'
    language: str = 'english'

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

    def to_bibtex(self):


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
        
        stream.write(self.conference.conference_status.value)
        stream.write('{')
        stream.write(f'{{{first_last_name}}}:{self.conference.conference_code.lower()}-{self.reference.paper_id.lower()},\n')
        stream.write(f'author = {{{authors}}}\n')
        stream.write(f'title = {{{self.reference.title}}},\n')
        if self.reference.pages is not None:
            stream.write(f'pages = {{{self.reference.pages}}},\n')
        else:
            stream.write('pages = {},\n')
        stream.write(f'paper = {{{self.reference.paper}}},\n')
        stream.write(f'venue = {{{self.reference.venue}}},\n')
        stream.write(f'publisher = {{{self.publisher}}},\n')
        stream.write(f'url = {{{self.reference.url}}},\n')
        stream.write(f'language = {{{self.language}}}\n')
        stream.write('}')

        return stream.getvalue()

        # return f"""
        #     @inproceedings{{{first_last_name}:{self.conference.conference_code}-{self.reference.paper_id},
        #         author = {{{authors}}}   
        #         title = {{{self.reference.title}}},
        #         pages = {{{self.reference.pages if self.reference.pages else ''}}},
        #         paper = {{{self.reference.paper}}},
        #         venue = {{{self.reference.venue}}},
        #         publisher = {{{self.publisher}}},
        #         url = {{{self.reference.url}}},
        #         language = {{{self.language}}}
        #     }}
        # """

    def to_latex(self):

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
            %cite{{{first_last_name}}}:{self.conference.conference_code}-{self.reference.paper_id}
            \\bibitem{{{first_last_name}}}:{self.conference.conference_code}-{self.reference.paper_id}
            {authors},
            \\textquotedblleft{{{self.reference.title}}}\\textquotedblright,
            in \\emph{{{self.reference.book_title}}}, {self.reference.venue}, {self.reference.pages}
            \\url{{{self.reference.url}}}
        """

    def to_word():
        return ''
        