import logging as lg

import io

from anyio import Path

from meow.utils.datetime import format_datetime_full, format_datetime_time

from meow.services.local.event.final_proceedings.abstract_plugin.abstract_final_proceedings_plugin import AbstractFinalProceedingsPlugin


logger = lg.getLogger(__name__)


class MkdocsFinalProceedingsPlugin(AbstractFinalProceedingsPlugin):
    """ MkdocsFinalProceedingsPlugin """

    def __init__(self, final_proceedings: dict, working_dir: Path) -> None:
        self.final_proceedings = final_proceedings
        self.working_dir = working_dir

    async def prepare(self) -> None:
        mkdocs_yml = Path(self.working_dir, "mkdocs.yml")
        await mkdocs_yml.write_text(await get_mkdocs_yml_content(self.final_proceedings.get('event', None)))

    async def home(self) -> None:
        index_md = Path(self.working_dir, "src", "home.md")
        await index_md.write_text(await get_index_md_content(self.final_proceedings.get('event', None)))

    async def session(self) -> None:
        await create_final_proceedings_session(self.final_proceedings, self.working_dir)

    async def classification(self) -> None:
        await create_final_proceedings_classification(self.final_proceedings, self.working_dir)

    async def author(self) -> None:
        await create_final_proceedings_author(self.final_proceedings, self.working_dir)

    async def institute(self) -> None:
        await create_final_proceedings_institute(self.final_proceedings, self.working_dir)

    async def doi_per_institute(self) -> None:
        await create_final_proceedings_doi_per_institute(self.final_proceedings, self.working_dir)

    async def keyword(self) -> None:
        await create_final_proceedings_keyword(self.final_proceedings, self.working_dir)

    async def finalize(self) -> None:
        pass

    async def generate(self) -> io.BytesIO:
        b = io.BytesIO()

        b.seek(0)

        return b

    async def clean(self) -> None:
        pass




async def create_final_proceedings_keyword(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    keyword_dir = Path(src_dir, "keyword")
    await keyword_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_keyword', await keyword_dir.absolute())

    nav_md = Path(keyword_dir, "nav.md")
    await nav_md.write_text(await get_keyword_nav_md_content(final_proceedings))

    index_md = Path(keyword_dir, "index.md")
    await index_md.write_text(await get_keyword_index_md_content(final_proceedings))


async def create_final_proceedings_doi_per_institute(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    doi_per_institute_dir = Path(src_dir, "doi-per-institute")
    await doi_per_institute_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_doi_per_institute', await doi_per_institute_dir.absolute())

    nav_md = Path(doi_per_institute_dir, "nav.md")
    await nav_md.write_text(await get_doi_per_institute_nav_md_content(final_proceedings))

    index_md = Path(doi_per_institute_dir, "index.md")
    await index_md.write_text(await get_doi_per_institute_index_md_content(final_proceedings))


async def create_final_proceedings_institute(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    institute_dir = Path(src_dir, "institute")
    await institute_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_institute', await institute_dir.absolute())

    nav_md = Path(institute_dir, "nav.md")
    await nav_md.write_text(await get_institute_nav_md_content(final_proceedings))

    index_md = Path(institute_dir, "index.md")
    await index_md.write_text(await get_institute_index_md_content(final_proceedings))


async def create_final_proceedings_author(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    author_dir = Path(src_dir, "author")
    await author_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_author', await author_dir.absolute())

    nav_md = Path(author_dir, "nav.md")
    await nav_md.write_text(await get_author_nav_md_content(final_proceedings))

    index_md = Path(author_dir, "index.md")
    await index_md.write_text(await get_author_index_md_content(final_proceedings))


async def create_final_proceedings_classification(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    classification_dir = Path(src_dir, "classification")
    await classification_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_classification', await classification_dir.absolute())

    nav_md = Path(classification_dir, "nav.md")
    await nav_md.write_text(await get_classification_nav_md_content(final_proceedings))

    index_md = Path(classification_dir, "index.md")
    await index_md.write_text(await get_classification_index_md_content(final_proceedings))


async def create_final_proceedings_session(final_proceedings: dict, working_dir: Path):

    src_dir = Path(working_dir, "src")

    session_dir = Path(src_dir, "session")
    await session_dir.mkdir(parents=True, exist_ok=True)

    print('create_final_proceedings_sessions', await session_dir.absolute())

    nav_md = Path(session_dir, "nav.md")
    await nav_md.write_text(await get_session_nav_md_content(final_proceedings))

    index_md = Path(session_dir, "index.md")
    await index_md.write_text(await get_session_index_md_content(final_proceedings))

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')

        session_md = Path(session_dir, f"{session_code}.md")

        await session_md.write_text(await get_session_md_content(session))


async def get_doi_per_institute_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_doi_per_institute_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# DOI per Institute list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_keyword_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_keyword_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# Keyword list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_institute_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_institute_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# Institute list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_author_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_author_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# Author list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_classification_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_classification_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# Classification list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_session_nav_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("* [Index](index.md)\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_session_index_md_content(final_proceedings: dict) -> str:

    stream = io.StringIO()

    stream.write("# Session list\n")
    stream.write("\n")

    for session in final_proceedings.get('sessions', []):

        session_code = session.get('code', '')
        session_title: str = session.get('title', '')

        stream.write(f"* [{session_code} - {session_title}]")
        stream.write(f"({session_code}.md)\n")

    stream.write("\n")

    return stream.getvalue()


async def get_session_contribution_md_content(contribution: dict) -> str:

    stream = io.StringIO()

    contribution_code = contribution.get('code', '')

    stream.write(f"### {contribution_code}\n\n")
    stream.write(f"** {contribution.get('title', '')} **\n\n")
    stream.write(f"> {contribution.get('description', '')}\n\n")

    stream.write(f"- Slides: [{contribution_code}]")
    stream.write(f"(pdf/{contribution_code}.pdf) [5.143 MB]\n\n")

    stream.write(f"- DOI: reference for this paper")
    stream.write(f"※ https://doi.org/10.18429/JACoW-FEL2019-MOA01\n\n")

    stream.write(f"- About: paper received ※ 26 August 2019 - ")
    stream.write(f"paper accepted ※ 09 September 2019 - ")
    stream.write(f"issue date ※ 05 November 2019\n\n")

    stream.write(f"- Export: reference for this paper using")
    stream.write(f"※ BibTeX, ※ LaTeX, ※ Text/Word")
    stream.write(f"※ RIS, ※ EndNote (xml)\n\n")

    return stream.getvalue()


async def get_session_md_content(session: dict) -> str:

    stream = io.StringIO()

    session_code = session.get('code', '')
    session_title: str = session.get('title', '')

    session_start = format_datetime_full(session.get('start', None))
    session_end = format_datetime_time(session.get('end', None))

    stream.write(f"# {session_code} - {session_title}\n\n")
    stream.write(f"** {session_start} - {session_end} **\n\n")

    session_conveners = session.get('conveners', [])

    if len(session_conveners) > 0:

        stream.write("** Chair: ")

        for convener in session_conveners:
            stream.write(f"{convener.get('first')} {convener.get('last')}")
            stream.write(f"({convener.get('affiliation')})")

        stream.write("**\n\n")

    stream.write("\n\n")

    for contribution in session.get('contributions', []):
        stream.write(await get_session_contribution_md_content(contribution))

    return stream.getvalue()


async def get_mkdocs_yml_content(event: dict) -> str:
    return f""" 
site_name: {event.get('title')}
site_description: {event.get('title')} - {event.get('location')}
site_author: Author
copyright: Copyright &copy; 2016 - 2020 Martin Donath

docs_dir: src
site_dir: out

extra_css:
  - assets/css/extra.css

extra_javascript:
  - assets/js/extra.js

theme:
  name: material
  logo: assets/img/logo.png
  favicon: assets/img/favicon.png

  highlightjs: true

  icon:
    repo: fontawesome/brands/git-alt

  features:
    - navigation.indexes
    - toc.integrate
    - navigation.tabs
    - navigation.tabs.sticky

  font:
    code: Roboto Mono

  language: en

  palette:
    # Palette toggle for light mode
    - scheme: default
      primary: gray
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode

    # Palette toggle for dark mode
    - scheme: slate
      primary: gray
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:

  - 'section-index'
  
  - 'literate-nav':
      nav_file: nav.md
    
  - search:
      lang: en
      min_search_length: 3
      prebuild_index: true

      # full 	Indexes the title, section headings, and full text of each page.
      # sections 	Indexes the title and section headings of each page.
      # titles 	Indexes only the title of each page.
      indexing: 'titles'

extra:
  homepage: /

  generator: true

  social:
    - icon: fontawesome/brands/github
      name: squidfunk on Twitter
      link: https://twitter.com/squidfunk

  consent:
    title: Cookie consent
    actions:
      - accept
      - reject

    description: >-
      We use cookies to recognize your repeated visits and preferences, as well
      as to measure the effectiveness of our documentation and whether users
      find what they're searching for. With your consent, you're helping us to
      make our documentation better.

nav:
    - Home: index.md
    - Session: session/
    - Classification: classification/
    - Author: author/
    - Institute: institute/
    - DOI per Institute: doi-per-institute/
    - Keyword: keyword/
    
"""


async def get_index_md_content(event: dict) -> str:

    return f""" 
# Welcome {event.get('title')} - Trieste, Italy - August 22-26

## Proceedings of the 40th International Free Electron Laser Conference

For full documentation visit [{event.get('title')}]({event.get('url')}).

The links below lead to detailed listings of the many facets of the conference, 
including Portable Acrobat Format (PDF) files of all invited and contributed papers, 
together with slides from oral presentations.

For any information or request, please refer to [info@fel2022.org](info@fel2022.org).


## Index of papers by

- [Session](session)
- [Classification](classification)
- [Author](author)
- [Institute](institute)
- [DOI per Institute](doi-per-institute)
- [Keyword](keyword)


"""
