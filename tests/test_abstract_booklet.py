"""Abstract booklet generation against the Indico mock (no Indico, no Redis)."""

import base64
import io

import pytest
from odf import teletype
from odf.opendocument import load

from meow.tasks.infra.task_status import TaskStatus
from meow.tasks.local.event_abstract_booklet import EventAbstractBookletTask
from meow.services.local.event.abstract_booklet.create_abstract_booklet import (
    create_abstract_booklet_from_event,
)
from meow.services.local.event.abstract_booklet.export_abstract_booklet import (
    export_abstract_booklet_to_odt,
)

pytestmark = pytest.mark.anyio

TASK_ID = "test-abstract-booklet"


@pytest.fixture
def task():
    TaskStatus.start_task(TASK_ID)
    yield EventAbstractBookletTask(code="event_abstract_booklet", task_id=TASK_ID)
    TaskStatus.stop_task(TASK_ID)


async def run_task(task, params) -> list[dict]:
    return [r async for r in task.run(params)]


def booklet_text(result: dict) -> str:
    odt = load(io.BytesIO(base64.b64decode(result["b64"])))
    return teletype.extractText(odt.text)


async def test_progress_phases_and_result(task, task_params):
    events = await run_task(task, task_params)

    phases = [e["value"]["phase"] for e in events if e["type"] == "progress"]
    assert phases == [
        "collect_sessions_and_contributions",
        "create_abstract_booklet_from_event",
        "export_abstract_booklet_to_odt",
    ]

    assert events[-1]["type"] == "result"
    assert events[-1]["value"]["filename"].startswith("1_MOCK2026")
    assert events[-1]["value"]["filename"].endswith(".odt")


async def test_booklet_content(task, task_params):
    text = booklet_text((await run_task(task, task_params))[-1]["value"])

    # sessions and contributions, in timetable order
    positions = [
        text.index(s)
        for s in (
            "MOA - Opening Session",
            "MOA01",
            "First Light from the Mock Source",
            "MOA02",
            "MOP - Poster Session",
            "MOP01",
            "A Poster on Vacuum Systems",
        )
    ]
    assert positions == sorted(positions)

    # abstracts, including multi-line and special characters
    assert "The second paragraph of the abstract." in text
    assert "Beam Dynamics & Stability <Preliminary>" in text
    assert "special characters: & < > \" '." in text

    # session chair and unicode author names
    assert "Giulia Rossi" in text
    assert "Müller-Žďárský" in text


async def test_only_configured_custom_fields_are_rendered(task, task_params):
    text = booklet_text((await run_task(task, task_params))[-1]["value"])

    # settings.custom_fields = [Funding Agency]
    assert "Mock Foundation grant 42" in text
    assert "Footnote that must not appear" not in text


async def test_indico_requests(task, task_params, indico_mock):
    await run_task(task, task_params)

    base = "/event/1/manage/purr"
    assert sorted(indico_mock.mock.paths) == [
        f"{base}/abstract-booklet-contributions-data/11",
        f"{base}/abstract-booklet-contributions-data/12",
        f"{base}/abstract-booklet-sessions-data",
    ]
    # the session cookie received from the plugin is forwarded to Indico
    assert all(
        r.cookies.get("indico_session_http") == "test-session"
        for r in indico_mock.mock.requests
    )


async def test_rejected_by_indico_without_session(task, task_params, indico_mock):
    task_params["cookies"] = {"indico_session_http": ""}

    with pytest.raises(BaseException):
        await run_task(task, task_params)

    # it failed because the mock answered 403 to the very first call
    assert indico_mock.mock.paths == ["/event/1/manage/purr/abstract-booklet-sessions-data"]


async def test_duplicate_metadata_synchronisation_in_booklet():
    event = {
        "url": "http://mock-indico.invalid/event/1/",
        "title": "MOCK2026",
        "description": "Mock Conference",
        "location": "Trieste",
        "address": "SS 14",
        "timezone": "Europe/Rome",
    }
    session = {
        "id": 11,
        "code": "MOA",
        "title": "Opening Session",
        "session": {"code": "MOA"},
        "start_dt": {"date": "2026-05-10", "time": "09:00:00", "tz": "Europe/Rome"},
        "end_dt": {"date": "2026-05-10", "time": "12:00:00", "tz": "Europe/Rome"},
    }
    original_contrib = {
        "id": "1",
        "friendly_id": 1,
        "code": "MOA01",
        "session_id": 11,
        "start_dt": {"date": "2026-05-10", "time": "09:00:00", "tz": "Europe/Rome"},
        "end_dt": {"date": "2026-05-10", "time": "09:30:00", "tz": "Europe/Rome"},
        "title": "Synchronized Title from MOA01",
        "description": "Synchronized Abstract Description from MOA01.",
        "primary_authors": [
            {
                "id": "1",
                "first_name": "Anna",
                "last_name": "Bianchi",
                "affiliation": "Test Laboratory A",
                "multiple_affiliations": [],
            }
        ],
        "coauthors": [],
        "speakers": [],
        "field_values": [],
    }
    duplicate_contrib = {
        "id": "2",
        "friendly_id": 2,
        "code": "MOP01",
        "session_id": 11,
        "start_dt": {"date": "2026-05-10", "time": "09:30:00", "tz": "Europe/Rome"},
        "end_dt": {"date": "2026-05-10", "time": "10:00:00", "tz": "Europe/Rome"},
        "title": "Old Duplicate Title",
        "description": "Old Duplicate Abstract.",
        "primary_authors": [],
        "coauthors": [],
        "speakers": [],
        "field_values": [{"name": "CAT_duplicate_of", "value": "MOA01"}],
    }

    # 1. When enabled (default)
    contributions = [dict(original_contrib), dict(duplicate_contrib)]
    ab = await create_abstract_booklet_from_event(
        event,
        [session],
        contributions,
        settings={"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": True},
    )
    odt = export_abstract_booklet_to_odt(ab, {}, {})
    text = teletype.extractText(load(odt).text)
    # Both contributions should have the synchronized title and author
    assert "Synchronized Title from MOA01" in text
    assert text.count("Synchronized Title from MOA01") == 2
    assert "Old Duplicate Title" not in text

    # 2. When disabled via sync_duplicate_metadata=False
    contributions_disabled = [dict(original_contrib), dict(duplicate_contrib)]
    ab_disabled = await create_abstract_booklet_from_event(
        event,
        [session],
        contributions_disabled,
        settings={"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": False},
    )
    odt_disabled = export_abstract_booklet_to_odt(ab_disabled, {}, {})
    text_disabled = teletype.extractText(load(odt_disabled).text)
    assert "Old Duplicate Title" in text_disabled
    assert text_disabled.count("Synchronized Title from MOA01") == 1
