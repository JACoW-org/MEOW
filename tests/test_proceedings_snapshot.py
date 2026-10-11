"""Pre-press and final proceedings of a real event, served from a snapshot.

Skipped unless ``MEOW_INDICO_SNAPSHOT`` points to a snapshot directory (see
docs/TESTING.md). No Indico and no Redis: Indico is the mock, Redis is
fakeredis. The expectations are consistency checks between the generated files,
so they hold for any event.
"""

import json
from pathlib import Path

import fitz
import pytest

from meow.tasks.infra.task_status import TaskStatus
from meow.tasks.local.event_final_proceedings import EventFinalProceedingsTask
from meow.tasks.local.event_pre_press_proceedings import EventPrePressProceedingsTask

pytestmark = pytest.mark.anyio

TASK_ID = "test-proceedings-snapshot"

TASKS = {
    "prepress": EventPrePressProceedingsTask,
    "final": EventFinalProceedingsTask,
}
# marker file created in var/html/<event_id>/ by the static site generation
MARKERS = {"prepress": "prepress", "final": "proceedings"}


async def run_task(kind: str, params: dict) -> list[dict]:
    # The license icon is hosted outside Indico (creativecommons.org): the
    # pipeline would download it, and tests must not need the network.
    params["settings"]["paper_license_icon_url"] = ""

    TaskStatus.start_task(TASK_ID)
    try:
        task = TASKS[kind](code=kind, task_id=TASK_ID)
        return [e async for e in task.run(params)]
    finally:
        TaskStatus.stop_task(TASK_ID)


def read_references(html: Path) -> list[dict]:
    """Per-contribution records (the first line describes the event)."""
    [jsonl] = (html / "json").glob("references-*.jsonl")
    lines = jsonl.read_text().splitlines()
    return [json.loads(line) for line in lines[1:]]


@pytest.mark.parametrize("kind", ["prepress", "final"])
async def test_proceedings_are_generated(kind, snapshot_task_params, meow_workdir):
    event_id = snapshot_task_params["event"]["id"]

    events = await run_task(kind, snapshot_task_params)

    # every declared step ran, in order, and the task ended with its result
    declared = next(
        e["value"]["tasks"] for e in events
        if e["type"] == "progress" and e["value"].get("phase") == "init_tasks_list"
    )
    phases = [
        e["value"]["phase"] for e in events
        if e["type"] == "progress" and e["value"]["phase"] != "init_tasks_list"
    ]
    assert phases == [t.code for t in declared]
    assert events[-1]["type"] == "result"
    assert events[-1]["value"]["event_code"] == event_id

    html = meow_workdir / "var" / "html" / event_id
    assert (html / "index.html").is_file()
    assert (html / MARKERS[kind]).exists()

    # papers: those that were included, and only those, are in the site
    pdfs = {p.stem: p for p in (html / "pdf").glob("*.pdf")}
    [volume] = [p for n, p in pdfs.items() if n.endswith("_proceedings_volume")]
    [brief] = [p for n, p in pdfs.items() if n.endswith("_proceedings_brief")]
    papers = {
        n: p for n, p in pdfs.items()
        if not n.endswith(("_proceedings_volume", "_proceedings_brief"))
    }
    included = [r for r in read_references(html) if r["position"] != "0-0"]
    assert papers
    assert {r["paperId"] for r in included} == set(papers)

    # position "start-end" in the volume is consistent with the paper's pages
    for r in included:
        start, end = map(int, r["position"].split("-"))
        assert end - start == fitz.open(papers[r["paperId"]]).page_count, r["paperId"]

    # the volume contains every paper; the brief has one page per paper
    paper_pages = sum(fitz.open(p).page_count for p in papers.values())
    assert fitz.open(volume).page_count >= paper_pages
    assert fitz.open(brief).page_count == len(papers)

    # every included paper is listed in a session page
    session_pages = "".join(p.read_text() for p in (html / "session").rglob("*.html"))
    assert [r["paperId"] for r in included if r["paperId"] not in session_pages] == []
