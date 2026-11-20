"""Chair line of a session in the abstract booklet (CAT#48)."""

import pytest
from odf import teletype
from odf.opendocument import load
from odf.text import P

from meow.services.local.event.abstract_booklet.create_abstract_booklet import (
    create_abstract_booklet_from_event,
)
from meow.services.local.event.abstract_booklet.export_abstract_booklet import (
    export_abstract_booklet_to_odt,
)

pytestmark = pytest.mark.anyio

EVENT = {
    "id": 1,
    "title": "MOCK2026",
    "description": "Mock Conference",
    "location": "Trieste",
    "address": "SS 14",
    "timezone": "Europe/Rome",
}


def convener(first: str, last: str, affiliation: str = "", linked: list[str] | None = None):
    return {
        "first_name": first,
        "last_name": last,
        "affiliation": affiliation,
        "multiple_affiliations": linked or [],
    }


async def chair_line(conveners: list[dict]) -> str:
    session = {
        "id": 11,
        "code": "MOA",
        "title": "Opening Session",
        "session": {"code": "MOA"},
        "start_dt": {"date": "2026-05-10", "time": "09:00:00", "tz": "Europe/Rome"},
        "end_dt": {"date": "2026-05-10", "time": "12:00:00", "tz": "Europe/Rome"},
        "conveners": conveners,
    }
    ab = await create_abstract_booklet_from_event(EVENT, [session], [], settings={})
    doc = load(export_abstract_booklet_to_odt(ab, {}, {}))
    paragraphs = [teletype.extractText(p) for p in doc.text.getElementsByType(P)]
    [line] = [text for text in paragraphs if text.startswith("Chair:")]
    return line


async def test_convener_with_affiliations():
    assert await chair_line([convener("Jane", "Doe", "CERN")]) == "Chair: Jane Doe (CERN)"


async def test_convener_without_affiliations_is_printed():
    assert await chair_line([convener("Jane", "Doe")]) == "Chair: Jane Doe"


async def test_conveners_are_separated():
    line = await chair_line(
        [convener("Jane", "Doe", "CERN"), convener("John", "Roe"), convener("Ann", "Poe", "DESY")]
    )

    assert line == "Chair: Jane Doe (CERN), John Roe, Ann Poe (DESY)"
