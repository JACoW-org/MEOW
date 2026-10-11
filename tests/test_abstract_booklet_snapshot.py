"""Abstract booklet of a real event, served from a snapshot (see docs/TESTING.md).

Skipped unless ``MEOW_INDICO_SNAPSHOT`` points to a snapshot directory. The
expectations are derived from the snapshot itself, so any event works.
"""

import base64
import hashlib
import io
import json

import aiohttp
import pytest
from odf import teletype
from odf.opendocument import load

from meow.tasks.infra.task_status import TaskStatus
from meow.tasks.local.event_abstract_booklet import EventAbstractBookletTask

pytestmark = pytest.mark.anyio

TASK_ID = "test-abstract-booklet-snapshot"


async def test_every_session_and_contribution_is_in_the_booklet(
    snapshot_mock, snapshot_task_params
):
    purr = next(snapshot_mock.mock.fixture_dir.glob("event/*/manage/purr"))
    sessions = json.loads((purr / "abstract-booklet-sessions-data.json").read_text())["sessions"]
    codes = [
        c["code"]
        for s in sessions
        for c in json.loads(
            (purr / f"abstract-booklet-contributions-data/{s['id']}.json").read_text()
        )["contributions"]
    ]
    assert sessions and codes

    TaskStatus.start_task(TASK_ID)
    try:
        task = EventAbstractBookletTask(code="event_abstract_booklet", task_id=TASK_ID)
        events = [e async for e in task.run(snapshot_task_params)]
    finally:
        TaskStatus.stop_task(TASK_ID)

    result = events[-1]
    assert result["type"] == "result"
    odt = load(io.BytesIO(base64.b64decode(result["value"]["b64"])))
    text = teletype.extractText(odt.text)

    # sessions of the same block code (e.g. two MOA slots) are listed once per slot
    for session in sessions:
        assert session["title"] in text
    missing = [code for code in codes if code not in text]
    assert not missing


async def test_mock_serves_snapshot_files_with_the_md5_indico_reported(snapshot_mock):
    manifest = json.loads((snapshot_mock.mock.fixture_dir / "snapshot.json").read_text())
    assert manifest["files"]

    async with aiohttp.ClientSession(
        cookies={"indico_session_http": "test-session"}
    ) as client:
        for path, info in manifest["files"].items():
            async with client.get(snapshot_mock.base_url + path) as resp:
                assert resp.status == 200, path
                assert hashlib.md5(await resp.read()).hexdigest() == info["md5sum"], path
