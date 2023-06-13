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
    editors: list = field(default_factory=list)
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
    start_page: str = field(default='')
    end_page: str = field(default='')
    pages: str = field(default='')
    num_of_pages: int = field(default=0)

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
        ), dict(
            subject='',
            lang='en-us'
        )]

        attributes['contributors'] = [dict(
            name='',
            contributorType='Editor',
            affiliation=[dict(
                name=''
            )],
            nameIdentifiers=[dict(
                nameIdentifier='',
                schemeUri='https://jacow.org',
                nameIdentifierScheme='JACoW-ID'
            )]
        ) for editor in self.editors]

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
            relationType='isPartOf'
        ), dict(
            relatedIdentifier=self.issn,
            relatedIdentifierType='ISSN',
            relationType='isPartOf'
        )]

        attributes['sizes'] = [
            f"{self.pages} pages",
            # f"{self.file_size} {self.file_size_unit}",
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

        # TODO: da aggiungere
        attributes['landingPage'] = dict()

        attributes['url'] = 'https://schema.datacite.org/meta/kernel-4.0/index.html'

        attributes['schemaVersion'] = 'http://datacite.org/schema/kernel-4'

        return attributes
