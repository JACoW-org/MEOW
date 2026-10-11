"""Generate pre-press / final proceedings from a snapshot, offline.

Runs the same task the Indico plugin triggers, against the Indico mock serving
a snapshot (see ``tools/snapshot_indico.py``), with in-memory Redis. The output
is kept in ``--workdir``::

    <workdir>/var/html/<event_id>/         the static site (open index.html)
    <workdir>/var/html/<event_id>.7z       its archive (final proceedings)
    <workdir>/var/run/<event_id>_tmp/      downloaded PDFs (cache, reused by re-runs)

Usage::

    ./venv/bin/python tools/run_proceedings.py \\
        --snapshot var/snapshots/fel2024 --kind final --workdir var/work/fel2024
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def prepare_workdir(workdir: Path) -> None:
    """Scratch cwd linking the resources MEOW resolves relative to the cwd."""
    from tests.conftest import WORKDIR_LINKS

    workdir.mkdir(parents=True, exist_ok=True)
    for name in WORKDIR_LINKS:
        if not (workdir / name).exists():
            (workdir / name).symlink_to(REPO_ROOT / name)
    if not (workdir / "venv").exists():
        (workdir / "venv").symlink_to(sys.prefix)
    os.chdir(workdir)
    os.environ["PATH"] = f"{REPO_ROOT / 'bin'}{os.pathsep}{os.environ['PATH']}"


async def run(snapshot: Path, kind: str) -> int:
    from fakeredis import FakeAsyncRedis

    from meow.app.instances.databases import dbs
    from meow.tasks.infra.task_status import TaskStatus
    from meow.tasks.local.event_final_proceedings import EventFinalProceedingsTask
    from meow.tasks.local.event_pre_press_proceedings import (
        EventPrePressProceedingsTask,
    )
    from tests.conftest import build_task_params
    from tests.mock_indico.server import IndicoMockServer

    dbs.redis_client = FakeAsyncRedis(protocol=3)
    task_class = {"prepress": EventPrePressProceedingsTask,
                  "final": EventFinalProceedingsTask}[kind]

    with IndicoMockServer(snapshot) as server:
        params = build_task_params(server)
        # hosted outside Indico (creativecommons.org): do not need the network
        params["settings"]["paper_license_icon_url"] = ""
        event_id = params["event"]["id"]

        TaskStatus.start_task("run-proceedings")
        task = task_class(code=kind, task_id="run-proceedings")
        async for e in task.run(params):
            value = e["value"]
            if e["type"] == "progress" and value.get("phase") != "init_tasks_list":
                print(f"- {value['phase']}", flush=True)
            elif e["type"] == "log":
                print(f"  {value.severity.name}: {value.message}", flush=True)
            elif e["type"] == "result":
                print(f"result: {value}")

    html = Path("var", "html", event_id).resolve()
    print(f"\nsite:    {html / 'index.html'}")
    archive = html.with_suffix(".7z")
    if archive.exists():
        print(f"archive: {archive}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--kind", choices=["prepress", "final"], default="final")
    parser.add_argument("--workdir", required=True, type=Path)
    args = parser.parse_args()

    snapshot = args.snapshot.resolve()  # before changing directory
    prepare_workdir(args.workdir.resolve())
    sys.exit(asyncio.run(run(snapshot, args.kind)))
