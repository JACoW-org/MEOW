import logging as lg

from typing import Any

from datetime import datetime
from meow.models.local.event.final_proceedings.track_factory import track_data_factory

from meow.utils.datetime import datedict_to_tz_datetime
from meow.models.local.event.final_proceedings.event_factory import event_affiliation_factory, event_person_factory
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionFieldData, FileData, RevisionData


logger = lg.getLogger(__name__)


def contribution_data_factory(contribution: Any) -> ContributionData:
    contribution_data = ContributionData(
        code=contribution.get('code'),
        type=contribution.get('type'),
        url=contribution.get('url'),
        title=contribution.get('title'),
        duration=contribution.get('duration'),
        description=contribution.get('description'),
        session_code=contribution.get('session_code'),
        track=track_data_factory(
            contribution.get('track')
        ),
        keywords=list(set([])),
        authors=list(set([
            event_person_factory(person)
            for person in contribution.get('primary_authors', [])
        ])),
        institutes=list(set([
            event_affiliation_factory(institute)
            for institute in contribution.get('institutes', [])
        ])),
        room=contribution.get('room'),
        location=contribution.get('location'),
        field_values=[
            contribution_field_factory(field)
            for field in contribution.get('field_values')
        ],
        start=datedict_to_tz_datetime(
            contribution.get('start_dt')
        ),
        end=datedict_to_tz_datetime(
            contribution.get('end_dt')
        ),
        reception=datedict_to_tz_datetime(
            contribution.get('reception_dt')
        ) if 'reception_dt' in contribution else datetime.now(),
        acceptance=datedict_to_tz_datetime(
            contribution.get('acceptance_dt')
        ) if 'acceptance_dt' in contribution else datetime.now(),
        issuance=datedict_to_tz_datetime(
            contribution.get('issuance_dt')
        ) if 'issuance_dt' in contribution else datetime.now(),
        speakers=[
            event_person_factory(person)
            for person in contribution.get('speakers', [])
        ],
        primary_authors=[
            event_person_factory(person)
            for person in contribution.get('primary_authors', [])
        ],
        coauthors=[
            event_person_factory(person)
            for person in contribution.get('coauthors', [])
        ],
        editor=event_person_factory(contribution.get('editor'))
        if contribution.get('editor') else None,
        all_revisions=[
            contribution_revision_factory(revision)
            for revision in contribution.get('all_revisions', [])
        ],
        latest_revision=contribution_revision_factory(
            contribution.get('latest_revision', None)
        ) if contribution.get('latest_revision', None) else None
    )

    # logger.info("")
    # logger.info("CONTRIBUTION")
    # logger.info(json_encode(contribution_data.as_dict()))
    #
    # logger.info("")
    # logger.info("CONTRIBUTION - track")
    # logger.info(json_encode(contribution_data.track))
    #
    # logger.info("")
    # logger.info("CONTRIBUTION - authors")
    # logger.info(json_encode(contribution_data.authors))
    #
    # logger.info("")
    # logger.info("CONTRIBUTION - institutes")
    # logger.info(json_encode(contribution_data.institutes))
    #
    # logger.info("")
    # logger.info("")

    return contribution_data


def contribution_revision_factory(revision: Any) -> RevisionData:
    return RevisionData(
        id=revision.get('id'),
        comment=revision.get('comment'),
        files=[
            contribution_file_factory(file)
            for file in revision.get('files')
        ]
    )


def contribution_file_factory(file: Any) -> FileData:
    
    file_type = "paper" if file.get('file_type').get('type') == 1 else "slide"
    
    return FileData(
        file_type=file_type,
        uuid=file.get('uuid'),
        md5sum=file.get('md5sum'),
        filename=file.get('filename'),
        content_type=file.get('content_type'),
        download_url=file.get('download_url'),
        external_download_url=file.get('external_download_url'),
    )


def contribution_field_factory(field: Any) -> ContributionFieldData:
    return ContributionFieldData(
        name=field.get('name'),
        value=field.get('value'),
    )
