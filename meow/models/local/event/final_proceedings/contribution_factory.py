import logging as lg

from typing import Any

from datetime import datetime
from meow.models.local.event.final_proceedings.track_factory import track_data_factory

from meow.utils.datetime import datedict_to_tz_datetime
from meow.models.local.event.final_proceedings.event_factory import event_affiliation_factory, event_person_factory
from meow.models.local.event.final_proceedings.contribution_model import ContributionData, ContributionFieldData, EditableData, FileData, RevisionData, TagData
from meow.utils.serialization import json_encode
from meow.utils.sort import sort_revision_list_by_date

from pydash import find

logger = lg.getLogger(__name__)


def contribution_editable_factory(editable: Any) -> EditableData | None:

    if editable is None:
        return None

    all_revisions = [
        contribution_revision_factory(revision)
        for revision in editable.get('all_revisions', [])
        if revision is not None
    ]

    all_revisions.sort(key=sort_revision_list_by_date)

    latest_revision = contribution_revision_factory(
        editable.get('latest_revision', None)
    ) if editable.get('latest_revision', None) else None

    return EditableData(
        id=editable.get('id'),
        type=editable.get('type'),
        all_revisions=all_revisions,
        latest_revision=latest_revision
    )


def contribution_data_factory(contribution: Any) -> ContributionData:

    editables: list = contribution.get('editables', [])

    paper: Any = find(editables, lambda x: x.get('type', 0) ==
                      EditableData.EditableType.paper)
    slides: Any = find(editables, lambda x: x.get('type', 0) ==
                       EditableData.EditableType.slides)
    poster: Any = find(editables, lambda x: x.get('type', 0) ==
                       EditableData.EditableType.poster)

    paper_data: EditableData | None = contribution_editable_factory(paper)
    slides_data: EditableData | None = contribution_editable_factory(slides)
    poster_data: EditableData | None = contribution_editable_factory(poster)

    reception_revisions = [
        r for r in paper_data.all_revisions
        if r.initial_state == RevisionData.InitialRevisionState.new
    ] if paper_data else []

    reception_revision = reception_revisions[0] \
        if len(reception_revisions) else None

    revisitation_revisions = [
        r for r in paper_data.all_revisions
        if r.final_state == RevisionData.FinalRevisionState.accepted
    ] if paper_data else []

    revisitation_revision = revisitation_revisions[0] \
        if len(revisitation_revisions) else None

    acceptance_revisions = [
        r for r in paper_data.all_revisions
        if r.is_qa_approved
    ] if paper_data else []

    acceptance_revision = acceptance_revisions[0] \
        if len(acceptance_revisions) else None

    """ """

    reception = reception_revision.creation_date \
        if reception_revision is not None else None

    revisitation = revisitation_revision.creation_date \
        if revisitation_revision is not None else None

    acceptance = acceptance_revision.creation_date \
        if acceptance_revision is not None else None

    issuance = datetime.now()

    """ """

    # - #28 WEXB2 - Green only
    # - #226 TUOAA226 - Green & QA
    # - #222 TUOAB222 - Green & QA
    # - #44 WEXB1 - Green & QA & QA failed

    # [WEXB2]
    # Green Only:
    # TAG {
    #     "code": "QA02",
    #     "color": "yellow",
    #     "system": true,
    #     "title": "QA Pending"
    # }

    # [TUOAA226]
    # Green & QA:
    # TAG {
    #   "code": "QA01",
    #   "color": "green",
    #   "system": true,
    #   "title": "QA Approved"
    # }

    # [TUOAB222]
    # Green & QA:
    # TAG {
    #   "code": "QA01",
    #   "color": "green",
    #   "system": true,
    #   "title": "QA Approved"
    # }

    # [WEXB1]
    # Green & QA:
    # NO TAG
    
    # logger.info(f"contribution_code: {contribution.get('code')}")
    
    # logger.info(paper_data.all_revisions if paper_data else [])

    is_qa_approved = len([
        r for r in paper_data.all_revisions
        if r.is_qa_approved
    ] if paper_data else []) > 0
    
    is_qa_pending = len([
        r for r in paper_data.all_revisions
        if r.is_qa_pending
    ] if paper_data else []) > 0
    
    # logger.info(f"is_qa_approved: {is_qa_approved}")
    
    # logger.info("\n\n")

    """ """

    # received: paper uploded ($revision['created_dt'])
    # revised: paper edited ($revision['final_state']['name'] == "accepted")
    # accepted: qa ok
    # issue: date of proceedings

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
        is_qa_approved=is_qa_approved,
        is_qa_pending=is_qa_pending,
        paper=paper_data,
        slides=slides_data,
        poster=poster_data,
        reception=reception,
        revisitation=revisitation,
        acceptance=acceptance,
        issuance=issuance,
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
        ]
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
        initial_state=revision.get('initial_state'),
        final_state=revision.get('final_state'),
        creation_date=datedict_to_tz_datetime(
            revision.get('created_dt')
        ),
        files=[
            contribution_file_factory(file)
            for file in revision.get('files', [])
        ],
        tags=[
            contribution_tag_factory(tag)
            for tag in revision.get('tags', [])
        ]
    )


def contribution_file_factory(file: Any) -> FileData:

    file_type: int = file.get('file_type', None).get('type') \
        if file.get('file_type', None) else 0

    return FileData(
        file_type=file_type,
        uuid=file.get('uuid'),
        md5sum=file.get('md5sum'),
        filename=file.get('filename'),
        content_type=file.get('content_type'),
        download_url=file.get('download_url'),
        external_download_url=file.get('external_download_url'),
    )


def contribution_tag_factory(tag: Any) -> TagData:
    return TagData(
        code=tag.get('code'),
        color=tag.get('color'),
        system=tag.get('system'),
        title=tag.get('title'),
    )


def contribution_field_factory(field: Any) -> ContributionFieldData:
    return ContributionFieldData(
        name=field.get('name'),
        value=field.get('value'),
    )
