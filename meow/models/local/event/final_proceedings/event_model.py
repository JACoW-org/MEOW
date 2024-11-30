from dataclasses import dataclass, field, asdict
from datetime import datetime

from meow.utils.slug import slugify


@dataclass(kw_only=True, slots=True)
class PersonData:
    """ """

    id: str
    first: str
    last: str
    affiliations: set[str]
    email: str

    @property
    def code(self) -> str:
        return slugify(f"{self.id} {self.first} {self.last}")

    @property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @property
    def short(self) -> str:
        return f"{f'{self.first[0]}.' if len(self.first) > 0 else ''} {self.last}"

    @property
    def long(self) -> str:
        return f"{self.first} {self.last} ({self.affiliations_str})"
    
    @property
    def affiliations_str(self) -> str:
        affiliations_str = ", ".join(self.affiliations)
        return affiliations_str

    def __eq__(self, other: 'PersonData'):
        return (
            self.first == other.first and
            self.last == other.last and
            # set(self.affiliations) == set(other.affiliations) and
            self.id == other.id
        )

    def __hash__(self):
        return hash(('first', self.first,
                     'last', self.last,
                     'affiliations', ','.join(self.affiliations),
                     'id', self.id))

    def as_dict(self) -> dict:
        return {
            **asdict(self),
            "name": self.name,
            "short": self.short,
            "long": self.long,
            "code": self.code,
        }
    
    def sort_key(self):
        sorted_affiliations = sorted(self.affiliations)
        affiliations = " ".join(sorted_affiliations).lower()
        return f"{self.last} {self.first} {affiliations}"


@dataclass(kw_only=True, slots=True)
class AffiliationData:

    id: str
    name: str
    street: str
    postcode: str
    city: str
    country_code: str

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class KeywordData:

    code: str
    name: str

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(('code', self.code))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class MaterialData:

    file_type: str
    content_type: str
    filename: str
    md5sum: str
    size: int

    title: str
    description: str
    external_download_url: str
    section: str = field(default='')
    index: int = field(default=0)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class EventData:
    """ """

    id: str
    name: str
    title: str
    hosted: str
    timezone: str
    editorial: str
    location: str
    date: str
    isbn: str
    issn: str
    color: str

    series: str
    series_number: str

    copyright_year: str

    site_license_text: str
    site_license_url: str

    paper_license_icon_url: str
    paper_license_text: str

    doi_url: str
    doi_label: str

    start: datetime
    end: datetime

    @property
    def path(self) -> str:
        return slugify(self.name)

    @property
    def doi_code(self) -> str:
        return slugify(self.name).upper()

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id,
                     'title', self.title,
                     'path', self.path))

    def as_dict(self) -> dict:
        return {
            **
            asdict(self),
            "path": self.path,
        }
