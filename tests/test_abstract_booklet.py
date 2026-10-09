"""Abstract booklet generation against the Indico mock (no Indico, no Redis)."""

import base64
import io

import pytest
from odf import teletype
from odf.opendocument import load

from meow.tasks.infra.task_status import TaskStatus
from meow.tasks.local.event_abstract_booklet import EventAbstractBookletTask

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
