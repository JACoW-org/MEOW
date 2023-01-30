
from io import StringIO

class Citation:

    # constants
    publisher = 'JaCoW Publishing, Geneva, Switzerland'
    language = 'english'

    def __init__(self,
            conference_code,
            paper_id,
            authors,
            title,
            book_title,
            pages,
            paper,
            venue,
            url) -> None:

        self.conference_code = conference_code
        self.paper_id = paper_id
        self.authors = authors
        self.title = title
        self.book_title = book_title
        self.pages = pages
        self.paper = paper
        self.venue = venue
        self.url = url

    def to_bibtex(self) -> str:

        first_last_name = None
        if len(self.authors) > 0:
            first_last_name = self.authors[0].get('last_name').lower()

        authors = ''
        for index, author in enumerate(self.authors):
            if index > 0:
                authors += ' and '
            first_name = author.get('first_name')
            last_name = author.get('last_name')
            authors += f'{first_name[0].upper()}. {last_name}'

        return f"""
            @inproceedings{{{first_last_name}:{self.conference_code}-{self.paper_id},
                author = {{{authors}}},
                title = {{{self.title}}},
                pages = {{{self.pages}}},
                paper = {{{self.paper}}},
                venue = {{{self.venue}}},
                publisher = {{{self.publisher}}},
                url = {{{self.url}}},
                language = {{{self.language}}}
            }}
        """

    def to_latex(self) -> str:

        first_last_name = None
        if len(self.authors) > 0:
            first_last_name = self.authors[0].get('last_name').lower()

        authors = ''
        for index, author in enumerate(self.authors):
            if index > 0:
                authors += ' and '
            first_name = author.get('first_name')
            last_name = author.get('last_name')
            authors += f'{first_name[0].upper()}. {last_name}'

        return f"""
            %cite{{{first_last_name}}}:{self.conference_code}-{self.paper_id}
            \\bibitem{{{first_last_name}}}:{self.conference_code}-{self.paper_id}
            {authors},
            \\textquotedblleft{{{self.title}}}\\textquotedblright,
            in \\emph{{{self.book_title}}}, {self.venue}, {self.pages}
            \\url{{{self.url}}}
        """

    def to_word(self) -> str:
        return ""
    
    def to_ris(self) -> str:
        return ""
    
    def to_xml(self) -> str:
        return ""
        