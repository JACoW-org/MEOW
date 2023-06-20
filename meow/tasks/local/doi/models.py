from dataclasses import dataclass, field, asdict
from typing import Optional
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
    reference: Optional[Reference] = field(default=None)  #  BibTeX, LaTeX, Text/Word, RIS, EndNote
    conference_code: str = field(default='')
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
    doi_url: str = field(default='')
    doi_label: str = field(default='')
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

    @property
    def paper_size_mb(self) -> float:
        paper_size_mb_full = self.paper_size / (1024*1024)
        return float('{:.2g}'.format(paper_size_mb_full)) if paper_size_mb_full < 100 else float('{:.3g}'.format(paper_size_mb_full))

    def as_dict(self) -> dict:
        return asdict(self)
    
    def as_json(self) -> str:

        data = dict()

        data['id'] = self.doi_identifier
        data['type'] = 'dois'

        data['attributes'] = self._build_doi_attributes()

        return json.dumps(dict(data=data))
    
    def _build_doi_attributes(self) -> dict:

        attributes = dict()

        attributes['doi'] = self.doi_identifier

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
            resourceTypeGeneral='Text',
            resourceType='ConferencePaper'
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
            rights='CC 3.0',
            rightsUri='https://creativecommons.org/licenses/by/3.0',
            lang='en-us'
        )]

        attributes['descriptions'] = [dict(
            description=self.abstract,
            descriptionType='Abstract',
            lang='en-us'
        )]

        attributes['url'] = self.doi_landing_page

        attributes['schemaVersion'] = 'http://datacite.org/schema/kernel-4'

        return attributes
