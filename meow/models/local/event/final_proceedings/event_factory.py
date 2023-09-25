import logging as lg

from typing import Any

from meow.models.local.event.final_proceedings.event_model import (
    AffiliationData,
    MaterialData,
    EventData,
    KeywordData,
    PersonData,
)
from meow.utils.slug import slugify
from meow.utils.datetime import datedict_to_tz_datetime


logger = lg.getLogger(__name__)


def material_data_factory(material: Any) -> MaterialData:
    material_data = MaterialData(
        file_type=material.get("file_type"),
        content_type=material.get("content_type"),
        filename=material.get("filename"),
        md5sum=material.get("md5sum"),
        size=int(material.get("size")),
        title=material.get("title"),
        description=material.get("description"),
        external_download_url=material.get("external_download_url"),
        section=material.get('section'),
        index=material.get('index')
    )

    return material_data


def event_data_factory(event: Any, settings: dict) -> EventData:
    event_id = event.get("id", "")

    primary_color = settings.get("primary_color", "")

    title_short = settings.get("booktitle_short", "")
    title_long = settings.get("booktitle_long", "")

    hosted = settings.get("host_info", "")
    date = settings.get("date", "")
    location = settings.get("location", "")
    editorial = settings.get("editorial_board", "")
    isbn = settings.get("isbn", "")
    issn = settings.get("issn", "")

    doi_proto = settings.get("doi_proto", "https")
    doi_domain = settings.get("doi_domain", "doi.org")
    doi_context = settings.get("doi_context", "10.18429")
    doi_organization = settings.get("doi_organization", "JACoW")
    doi_conference = settings.get("doi_conference", "FEL2022")

    # https://doi.org/10.18429/JACoW-PCaPAC2022
    doi_url = f'{doi_proto}://{doi_domain}/{doi_context}/{doi_organization}-{doi_conference}'
    # DOI:10.18429/JACoW-PCaPAC2022
    doi_label = f'{doi_context}/{doi_organization}-{doi_conference}'

    series = settings.get("series", "")
    series_number = settings.get("series_number", "")

    start = datedict_to_tz_datetime(event.get("start_dt"))

    end = datedict_to_tz_datetime(event.get("end_dt"))

    event_data = EventData(
        id=event_id,
        color=primary_color,
        name=title_short,
        title=title_long,
        hosted=hosted,
        location=location,
        editorial=editorial,
        isbn=isbn,
        issn=issn,
        doi_url=doi_url,
        doi_label=doi_label,
        date=date,
        start=start,
        end=end,
        series=series,
        series_number=series_number,
    )

    # logger.info(event_data.as_dict())

    return event_data


def event_keyword_factory(keyword: str) -> KeywordData:
    keyword_data = KeywordData(code=slugify(keyword), name=keyword.strip())

    # logger.info(keyword_data.as_dict())

    return keyword_data


def event_person_factory(person: Any) -> PersonData:
    first = person.get("first_name").strip()
    last = person.get("last_name").strip()
    affiliation = person.get("affiliation").strip()
    email = person.get("email").strip() if person.get("email") else ""

    id = slugify("-".join([first, last, affiliation]))

    event_person_data = PersonData(
        id=id,
        first=first,
        last=last,
        affiliation=affiliation,
        email=email,
    )

    # logger.info(event_person_data.as_dict())

    return event_person_data


def event_affiliation_factory(affiliation: Any) -> AffiliationData:
    affiliation_data = AffiliationData(
        id=slugify(affiliation.get("name")),
        name=affiliation.get("name").strip(),
        city=affiliation.get("city"),
        country_code=affiliation.get("country_code"),
        postcode=affiliation.get("postcode"),
        street=affiliation.get("postcode"),
    )

    # logger.info(affiliation_data.as_dict())

    return affiliation_data
