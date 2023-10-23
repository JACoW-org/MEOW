from dataclasses import dataclass, field, asdict
from typing import Optional
from meow.tasks.local.doi.utils import paper_size_mb
from meow.tasks.local.reference.models import Reference

import json
import datetime


@dataclass
class AuthorsGroup:
    affiliation: str = field(default='')
    authors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuthorDOI:
    id: str = field(default='')
    first_name: str = field(default='')
    last_name: str = field(default='')
    affiliation: str = field(default='')

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class EditorDOI:
    first_name: str = field(default='')
    last_name: str = field(default='')
    affiliation: str = field(default='')

    def format(self):
        return f'{self.first_name} {self.last_name} ({self.affiliation})'

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContributionDOI:
    ''''''

    code: str = field(default='')
    title: str = field(default='')
    primary_authors: list[AuthorDOI] = field(default_factory=list[AuthorDOI])
    authors_groups: list[AuthorsGroup] = field(default_factory=list)
    abstract: str = field(default='')
    references: list = field(default_factory=list)
    paper_url: str = field(default='')
    slides_url: str = field(default='')
    # BibTeX, LaTeX, Text/Word, RIS, EndNote
    reference: Optional[Reference] = field(default=None)
    conference_code: str = field(default='')
    conference_doi_name: str = field(default='')
    series: str = field(default='')
    venue: str = field(default='')
    start_date: str = field(default='')
    end_date: str = field(default='')
    date: str = field(default='')
    publisher: str = field(default='JACoW Publishing')
    publisher_venue: str = field(default='Geneva, Switzerland')
    editors: list[EditorDOI] = field(default_factory=list)
    isbn: str = field(default='')
    issn: str = field(default='')
    reception_date: str = field(default='')
    revisitation_date: str = field(default='')
    acceptance_date: str = field(default='')
    issuance_date: str = field(default='')
    reception_date_iso: str = field(default='')
    revisitation_date_iso: str = field(default='')
    acceptance_date_iso: str = field(default='')
    issuance_date_iso: str = field(default='')
    doi_url: str = field(default='')
    doi_label: str = field(default='')
    doi_name: str = field(default='')
    doi_path: str = field(default='')
    doi_identifier: str = field(default='')
    doi_landing_page: str = field(default='')
    start_page: str = field(default='')
    end_page: str = field(default='')
    pages: str = field(default='')
    num_of_pages: int = field(default=0)
    paper_size: int = field(default=0)
    track: str = field(default='')
    subtrack: str = field(default='')
    keywords: list[str] = field(default_factory=list)

    @property
    def paper_size_mb(self) -> float:
        return paper_size_mb(self.paper_size)

    def as_dict(self) -> dict:
        return asdict(self)

    def as_json(self) -> str:

        data = dict()

        data['id'] = self.doi_identifier
        data['type'] = 'dois'

        data['attributes'] = self._build_doi_attributes()

        return json.dumps(dict(data=data))

    def as_hep_json(self) -> str:

        return json.dumps(self._build_hep_attributes())

    def _build_hep_attributes(self) -> dict:

        attributes = {
            "titles": [
                {
                    "source": "JACOW",
                    "title": self.title
                }
            ],
            "abstracts": [
                {
                    "source": "JACOW",
                    "value": self.abstract
                }
            ],
            "imprints": [
                {
                    "date": self.start_date
                }
            ],
            "keywords": [{
                "value": k,
                "source": "JACOW"
            } for k in self.keywords],
            "publication_info": [
                {
                    "artid": self.code,
                    "conf_acronym": self.conference_doi_name,
                    "journal_title": "JACoW",
                    "journal_volume": self.conference_doi_name,
                    "year": datetime.date.today().year
                }
            ],
            "dois": [
                {
                    "source": "JACOW",
                    "value": self.doi_name
                }
            ],
            "number_of_pages": self.num_of_pages,
            "document_type": [
                "conference paper"
            ],
            "documents": [
                {
                    "key": "document",
                    "fulltext": True,
                    "url": f"https://jacow.org/{self.conference_doi_name.lower()}/pdf/{self.code}.pdf",
                    "source": "JACOW"
                }
            ],
            "license": [
                {
                    "imposing": "JACOW",
                    "license": "CC-BY-4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0"
                }
            ],
            "authors": [
                {

                    "full_name": f"{editor.last_name}, {editor.first_name}",

                    "raw_affiliations": [
                        {
                            "value": editor.affiliation
                        }
                    ]
                }
                for editor in self.editors
            ],
            "_collections": [
                "Literature"
            ],
            "inspire_categories": [
                {
                    "term": "Accelerators"
                }
            ],
            "curated": False,
            "$schema": "https://inspirehep.net/schemas/records/hep.json",
            "citeable": True
        }

        return attributes

    def _build_doi_attributes(self) -> dict:

        attributes = dict()

        attributes['doi'] = self.doi_identifier

        attributes['event'] = 'draft'

        attributes['identifiers'] = [dict(
            identifierType='DOI',
            identifier=self.doi_url
        )]

        attributes['creators'] = [dict(
            name=f'{author.last_name},{author.first_name}',
            affiliation=[dict(
                name=author.affiliation
            )],
            nameIdentifiers=[dict(
                nameIdentifier=author.id,
                schemeUri='https://jacow.org',
                nameIdentifierScheme='JACoW-ID'
            )]
        ) for author in self.primary_authors]

        attributes['titles'] = [dict(
            title=self.title,
            lang='en-us'
        )]

        attributes['publisher'] = self.publisher

        attributes['publicationYear'] = datetime.date.today().year

        attributes['subjects'] = [dict(
            subject='Accelerator Physics',
            lang='en-us'
        )]

        if self.track:
            attributes['subjects'].append(dict(
                subject=self.track,
                lang='en-us'
            ))

        if self.subtrack:
            attributes['subjects'].append(dict(
                subject=self.subtrack,
                lang='en-us'
            ))

        attributes['contributors'] = [dict(
            name=f'{editor.last_name},{editor.first_name}',
            contributorType='Editor',
            affiliation=[dict(
                name=editor.affiliation
            )],
            nameIdentifiers=[dict(
                nameIdentifier=f'{index}',
                schemeUri='https://jacow.org',
                nameIdentifierScheme='JACoW-ID'
            )]
        ) for index, editor in enumerate(self.editors)]

        attributes['dates'] = [dict(
            date=self.reception_date,
            dateType='Submitted'
        ), dict(
            date=self.revisitation_date,
            dateType='Valid'
        ), dict(
            date=self.acceptance_date,
            dateType='Accepted'
        ), dict(
            date=self.issuance_date,
            dateType='Issued'
        )]

        attributes['language'] = 'en-us'

        attributes['types'] = dict(
            resourceTypeGeneral='ConferencePaper',
            resourceType='Text'
        )

        attributes['relatedIdentifiers'] = [dict(
            relatedIdentifier=self.isbn,
            relatedIdentifierType='ISBN',
            relationType='IsPartOf'
        ), dict(
            relatedIdentifier=self.issn,
            relatedIdentifierType='ISSN',
            relationType='IsPartOf'
        )]

        attributes['sizes'] = [
            f"{self.pages} pages",
            f"{self.paper_size_mb} MB",
        ]

        attributes['formats'] = ['PDF']

        attributes['rightsList'] = [dict(
            rights='Creative Commons Attribution 4.0 International',
            rightsUri='https://creativecommons.org/licenses/by/4.0/legalcode',
            lang='en-us',
            schemeUri='https://spdx.org/licenses/',
            rightsIdentifier='cc-by-4.0',
            rightsIdentifierScheme='SPDX'
        )]

        attributes['descriptions'] = [dict(
            description=self.abstract,
            descriptionType='Abstract',
            lang='en-us'
        )]

        attributes['url'] = self.doi_landing_page.lower()

        attributes['schemaVersion'] = 'http://datacite.org/schema/kernel-4'

        return attributes
