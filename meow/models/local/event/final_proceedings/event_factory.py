import logging as lg

from typing import Any

from meow.models.local.event.final_proceedings.event_model import AffiliationData, AttachmentData, EventData, KeywordData, PersonData
from meow.utils.slug import slugify
from meow.utils.datetime import datedict_to_tz_datetime


logger = lg.getLogger(__name__)


def attachment_data_factory(attachment: Any) -> AttachmentData:
    attachment_data = AttachmentData(
        file_type=attachment.get('file_type'),
        content_type=attachment.get('content_type'),
        filename=attachment.get('filename'),
        md5sum=attachment.get('md5sum'),
        size=int(attachment.get('size')),
        title=attachment.get('title'),
        description=attachment.get('description'),
        external_download_url=attachment.get('external_download_url'),
    )
    
    # logger.info(attachment_data.as_dict())

    return attachment_data


def event_data_factory(event: Any) -> EventData:
    event_data = EventData(
        id=event.get('id'),
        url=event.get('url'),
        title=event.get('title'),
        description=event.get('description'),
        location=event.get('location'),
        address=event.get('address'),
        start=datedict_to_tz_datetime(
            event.get('start_dt')
        ),
        end=datedict_to_tz_datetime(
            event.get('end_dt')
        ),
    )

    # logger.info(event_data.as_dict())

    return event_data


def event_keyword_factory(keyword: str) -> KeywordData:
    keyword_data = KeywordData(
        code=slugify(keyword),
        name=keyword.strip()
    )

    # logger.info(keyword_data.as_dict())

    return keyword_data


def event_person_factory(person: Any) -> PersonData:

    first = person.get('first_name').strip()
    last = person.get('last_name').strip()
    affiliation = person.get('affiliation').strip()
    email = person.get('email').strip() if person.get('email') else ''

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
        id=slugify(affiliation.get('name')),
        name=affiliation.get('name').strip(),
        city=affiliation.get('city'),
        country_code=affiliation.get('country_code'),
        postcode=affiliation.get('postcode'),
        street=affiliation.get('postcode'),
    )

    # logger.info(affiliation_data.as_dict())

    return affiliation_data
