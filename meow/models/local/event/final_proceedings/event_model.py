from dataclasses import dataclass, field, asdict
from datetime import datetime

from meow.utils.slug import slugify
from meow.models.local.event.final_proceedings.extract_initials import extract_initials


@dataclass(kw_only=True, slots=True)
class PersonData:
    """ """

    id: str
    first: str
    last: str
    affiliations: set[str]
    email: str
    # "single" (default) -> single first initial; "multiple" -> full initials (extract_initials).
    # Anything else falls back to the "single" behavior.
    initials_style: str = "multiple"

    @property
    def code(self) -> str:
        return slugify(f"{self.id} {self.first} {self.last}")

    @property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @property
    def short(self) -> str:
        # "multiple": For IPAC'26 use full initials
        if self.initials_style == "multiple":
            return f"{extract_initials(self.first)} {self.last}"
        # default ("single" or anything else): single first initial
        return f"{f'{self.first[0]}.' if len(self.first) > 0 else ''} {self.last}"
    
    @property
    def long(self) -> str:
        return f"{self.first} {self.last} ({self.affiliations_str})"

    @property
    def affiliations_str(self) -> str:
        affiliations_str = ", ".join(self.affiliations)
        return affiliations_str

    def __eq__(self, other: "PersonData"):
        return self.id == other.id

    def __hash__(self):
        return hash(("id", self.id))

    def as_dict(self) -> dict:
        data = asdict(self)
        # initials_style is configuration, not author data
        data.pop("initials_style", None)
        return {
            **data,
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
        return hash(("id", self.id))

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True, slots=True)
class KeywordData:
    code: str
    name: str

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(("code", self.code))

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
    section: str = field(default="")
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
        return hash(("id", self.id, "title", self.title, "path", self.path))

    def as_dict(self) -> dict:
        return {
            **asdict(self),
            "path": self.path,
        }

    def as_ref(self) -> dict:
        attributes = {
            "eventId": self.id,
            "code": self.name,
            "name": self.title,
            "location": self.location,
            "conferenceStart": str(self.start),
            "conferenceEnd": str(self.end),
            "date": self.date,
            "series": self.series,
            "seriesNumber": self.series_number,
            "copyrightYear": self.copyright_year,
            "doiCode": self.doi_code,
            # "useDoi": True,
            "baseUrl": f"https://jacow.org/{self.name}/",
            # "isPublished": False,
            "timestamp": str(datetime.now()),
        }

        if self.isbn != "":
            attributes["isbn"] = self.isbn

        if self.issn != "0000-0000":
            attributes["issn"] = self.issn

        return attributes
