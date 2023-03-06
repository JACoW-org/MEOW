import logging as lg

from typing import Any

import urllib

from meow.models.local.event.final_proceedings.track_model import TrackData, TrackGroupData
from meow.utils.slug import slugify


logger = lg.getLogger(__name__)


def track_data_factory(track: Any) -> TrackData | None:

    if track is None:
        return None

    track_code: str = track.get('code')
    track_title: str = track.get('title')
    track_description: str = track.get('description')
    track_position: int = track.get('position')
    track_group: str = track.get('group')

    track_code = slugify(track_title) \
        if not track_code else track_code

    track_data = TrackData(
        code=track_code,
        title=track_title,
        description=track_description,
        position=track_position,
        track_group=track_group_data_factory(track_group)
    )

    # logger.info(track_data.as_dict())

    return track_data


def track_group_data_factory(track_group) -> TrackGroupData | None:

    if track_group is None:
        return None

    track_group_code: str = track_group.get('code')
    track_group_title: str = track_group.get('title')
    track_group_description: str = track_group.get('description')
    track_group_position: int = track_group.get('position')

    track_group_code = slugify(track_group_title) \
        if not track_group_code else track_group_code

    track_group_data = TrackGroupData(
        code=track_group_code,
        title=track_group_title,
        description=track_group_description,
        position=track_group_position
    )

    # logger.info(track_group_data.as_dict())

    return track_group_data
