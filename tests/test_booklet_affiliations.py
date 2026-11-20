"""Affiliations in the abstract booklet follow the rule of the proceedings (CAT#47)."""

import pytest
from odf import teletype
from odf.opendocument import load

from meow.services.local.event.abstract_booklet.create_abstract_booklet import (
    _get_affiliations,
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
SESSION = {
    "id": 11,
    "code": "MOA",
    "title": "Opening Session",
    "session": {"code": "MOA"},
    "start_dt": {"date": "2026-05-10", "time": "09:00:00", "tz": "Europe/Rome"},
    "end_dt": {"date": "2026-05-10", "time": "12:00:00", "tz": "Europe/Rome"},
}


def person(first: str, last: str, affiliation: str, linked: list[str], id: str):
    return {
        "id": id,
        "first_name": first,
        "last_name": last,
        "affiliation": affiliation,
        "multiple_affiliations": linked,
    }


async def booklet_text(primary_authors: list[dict]) -> str:
    contribution = {
        "id": "1",
        "friendly_id": 1,
        "code": "MOA01",
        "session_id": 11,
        "start_dt": {"date": "2026-05-10", "time": "09:00:00", "tz": "Europe/Rome"},
        "end_dt": {"date": "2026-05-10", "time": "09:30:00", "tz": "Europe/Rome"},
        "title": "A title",
        "description": "An abstract.",
        "primary_authors": primary_authors,
        "coauthors": [],
        "speakers": [],
        "field_values": [],
    }
    ab = await create_abstract_booklet_from_event(EVENT, [SESSION], [contribution], settings={})
    return teletype.extractText(load(export_abstract_booklet_to_odt(ab, {}, {})).text)


def test_linked_affiliations_win_over_the_free_text():
    assert _get_affiliations("Paul Scherrer Institut", ["Paul Scherrer Institute"]) == {
        "Paul Scherrer Institute"
    }


def test_free_text_is_used_without_linked_affiliations_and_split_on_semicolon():
    assert _get_affiliations("Daresbury Laboratory;  Cockcroft Institute ", []) == {
        "Daresbury Laboratory",
        "Cockcroft Institute",
    }


def test_no_affiliation():
    assert _get_affiliations(None, []) == set()
    assert _get_affiliations("", None) == set()


async def test_booklet_shows_the_linked_affiliation_only():
    text = await booklet_text(
        [person("Jan", "Chrin", "Paul Scherrer Institut", ["Paul Scherrer Institute"], "1")]
    )

    assert "(Paul Scherrer Institute)" in text
    assert "Paul Scherrer Institut)" not in text and "Institut," not in text


async def test_booklet_splits_the_free_text_and_orders_the_affiliations():
    text = await booklet_text(
        [person("Rob", "Apsimon", "Lancaster University; Cockcroft Institute", [], "2")]
    )

    assert "(Cockcroft Institute, Lancaster University)" in text
    assert "Lancaster University; Cockcroft Institute" not in text


async def test_authors_of_the_same_institute_are_in_the_same_group():
    # the second one has the extra free text: with the old rule they were two groups
    text = await booklet_text(
        [
            person("Anna", "Bianchi", "GSI Helmholtz Centre", ["GSI Helmholtz Centre"], "1"),
            person("Carlo", "Rossi", "GSI Helmholtzzentrum", ["GSI Helmholtz Centre"], "2"),
        ]
    )

    assert text.count("(GSI Helmholtz Centre)") == 1
    assert "GSI Helmholtzzentrum" not in text
