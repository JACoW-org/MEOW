"""Snapshot the PURR endpoints (and files) MEOW consumes from a live Indico.

The output directory mirrors the URL tree of the Indico event, so it can be
served as-is by the test mock (``tests/mock_indico``)::

    <out>/snapshot.json
    <out>/event/1/manage/purr/settings-and-event-data.json
    <out>/event/1/manage/purr/final-proceedings-sessions-data.json
    <out>/event/1/manage/purr/final-proceedings-contributions-data/<block_id>.json
    <out>/event/1/manage/purr/abstract-booklet-...
    <out>/event/1/contributions/209/editing/paper/812/1478/MOBC03.pdf

JSON bodies are stored unchanged (apart from indentation and from the optional
subsetting); they still point to the original Indico host, which the mock
rewrites at serve time. Files are the ones MEOW downloads: the files of the
latest revision of each editable, and the event attachments. They are checked
against the ``md5sum`` Indico reports.

The snapshot contains personal data (author emails) and unpublished papers:
write it outside version control (e.g. under ``var/``).

Usage::

    export INDICO_SESSION=<value of the indico_session_http cookie>
    ./venv/bin/python tools/snapshot_indico.py \\
        --event-url http://indico:8000/event/1/ --out var/snapshots/fel2024

    # small subset: two sessions, three contributions each
    ... --sessions MOA MOB --max-contributions 3
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

import aiohttp

PURR = "manage/purr"
JSON_CONCURRENCY = 4
FILE_CONCURRENCY = 8
TIMEOUT = aiohttp.ClientTimeout(total=600)


class Crawler:
    def __init__(self, event_url: str, out: Path, session: str, quiet: bool = False):
        self.event_url = event_url if event_url.endswith("/") else event_url + "/"
        parts = urlsplit(self.event_url)
        self.origin = f"{parts.scheme}://{parts.netloc}"
        self.out = out
        self.quiet = quiet
        self.http = aiohttp.ClientSession(
            headers={
                "Cookie": f"indico_session_http={session}; indico_session={session}"
            },
            timeout=TIMEOUT,
        )
        self.json_sem = asyncio.Semaphore(JSON_CONCURRENCY)
        self.file_sem = asyncio.Semaphore(FILE_CONCURRENCY)
        self.errors: list[str] = []
        self.files: dict[str, dict] = {}

    def log(self, msg: str) -> None:
        if not self.quiet:
            print(msg, file=sys.stderr, flush=True)

    def local_path(self, url: str) -> Path:
        """Path (inside ``out``) mirroring the URL path."""
        path = unquote(urlsplit(url).path).lstrip("/")
        target = (self.out / path).resolve()
        if not target.is_relative_to(self.out.resolve()):
            raise ValueError(f"unsafe path in url: {url}")
        return target

    async def get_json(self, endpoint: str) -> dict:
        url = f"{self.event_url}{PURR}/{endpoint}"
        async with self.json_sem, self.http.get(url) as resp:
            if not resp.ok:
                raise RuntimeError(f"GET {url} -> {resp.status}")
            if "json" not in resp.content_type:
                raise RuntimeError(
                    f"GET {url} -> {resp.content_type} (invalid or expired session?)"
                )
            data = await resp.json()
        if isinstance(data, dict) and data.get("error") is True:
            raise RuntimeError(f"GET {url} -> {data}")
        return data

    def save_json(self, endpoint: str, data: dict) -> None:
        target = self.local_path(f"{self.event_url}{PURR}/{endpoint}.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    async def download(self, url: str, md5sum: str | None) -> None:
        target = self.local_path(url)
        if target.exists() and md5sum and _md5(target) == md5sum:
            self.log(f"cached    {target.name}")
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".part")
        try:
            async with self.file_sem, self.http.get(url) as resp:
                if not resp.ok:
                    raise RuntimeError(f"{resp.status}")
                with tmp.open("wb") as f:
                    async for chunk in resp.content.iter_chunked(64 * 1024):
                        f.write(chunk)
            if md5sum and _md5(tmp) != md5sum:
                raise RuntimeError("md5 mismatch")
            tmp.replace(target)
            self.log(f"downloaded {target.name}")
        except Exception as ex:
            tmp.unlink(missing_ok=True)
            self.errors.append(f"{url}: {ex}")
        else:
            self.files[urlsplit(url).path] = {
                "md5sum": md5sum,
                "size": target.stat().st_size,
            }

    async def run(
        self, session_filter: list[str], max_contributions: int | None, files: bool
    ) -> None:
        settings = await self.get_json("settings-and-event-data")
        self.save_json("settings-and-event-data", settings)
        event_title = settings["event"]["title"]
        self.log(f"event: {event_title}")

        sessions = None
        for kind in ("final-proceedings", "abstract-booklet"):
            data = await self.get_json(f"{kind}-sessions-data")
            if sessions is None:
                sessions = _filter_sessions(data["sessions"], session_filter)
            keep = {s["id"] for s in sessions}
            data["sessions"] = [s for s in data["sessions"] if s["id"] in keep]
            self.save_json(f"{kind}-sessions-data", data)
        assert sessions is not None
        self.log(f"sessions: {len(sessions)}")

        # same contributions subset for both kinds of export
        selected: dict[int, set] = {}

        async def contributions(kind: str, session: dict) -> list:
            sid = session["id"]
            data = await self.get_json(f"{kind}-contributions-data/{sid}")
            items = data["contributions"]
            if max_contributions is not None:
                if sid not in selected:
                    selected[sid] = {c["code"] for c in items[:max_contributions]}
                items = [c for c in items if c["code"] in selected[sid]]
                data["contributions"] = items
            self.save_json(f"{kind}-contributions-data/{sid}", data)
            return items

        # final-proceedings first: it defines the subset
        fp = await asyncio.gather(
            *(contributions("final-proceedings", s) for s in sessions)
        )
        await asyncio.gather(*(contributions("abstract-booklet", s) for s in sessions))
        n_contributions = sum(len(c) for c in fp)
        self.log(f"contributions: {n_contributions}")

        attachments = await self.get_json("final-proceedings-attachments-data")
        self.save_json("final-proceedings-attachments-data", attachments)

        to_download = [
            (a["external_download_url"], a.get("md5sum"))
            for a in attachments.get("attachments", [])
        ]
        for session_contributions in fp:
            for c in session_contributions:
                for editable in c.get("editables", []):
                    latest = editable.get("latest_revision") or {}
                    for f in latest.get("files", []):
                        to_download.append(
                            (f["external_download_url"], f.get("md5sum"))
                        )

        if files:
            self.log(f"files: {len(to_download)}")
            await asyncio.gather(*(self.download(u, m) for u, m in to_download))

        manifest = {
            "origin": self.origin,
            "event_url": self.event_url,
            "event_title": event_title,
            "crawled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sessions": len(sessions),
            "contributions": n_contributions,
            "files": dict(sorted(self.files.items())),
        }
        (self.out / "snapshot.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        )

    async def close(self) -> None:
        await self.http.close()


def _filter_sessions(sessions: list[dict], wanted: list[str]) -> list[dict]:
    if not wanted:
        return sessions
    selected = [s for s in sessions if s["code"] in wanted or str(s["id"]) in wanted]
    missing = set(wanted) - {s["code"] for s in selected} - {str(s["id"]) for s in selected}
    if missing:
        raise SystemExit(f"unknown sessions: {', '.join(sorted(missing))}")
    return selected


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


async def main(args: argparse.Namespace) -> int:
    session = args.session or os.environ.get("INDICO_SESSION", "")
    if not session:
        print("missing session: set INDICO_SESSION or pass --session", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    crawler = Crawler(args.event_url, args.out, session, args.quiet)
    try:
        await crawler.run(args.sessions, args.max_contributions, not args.no_files)
    finally:
        await crawler.close()

    for error in crawler.errors:
        print(f"ERROR {error}", file=sys.stderr)
    return 1 if crawler.errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--event-url", required=True, help="e.g. http://indico:8000/event/1/")
    parser.add_argument("--out", required=True, type=Path, help="output directory")
    parser.add_argument(
        "--session",
        help="value of the indico_session_http cookie (default: $INDICO_SESSION)",
    )
    parser.add_argument(
        "--sessions", nargs="*", default=[], metavar="CODE_OR_ID",
        help="only these session blocks (default: all)",
    )
    parser.add_argument(
        "--max-contributions", type=int, metavar="N",
        help="keep only the first N contributions of each session",
    )
    parser.add_argument("--no-files", action="store_true", help="skip PDFs/attachments")
    parser.add_argument("--quiet", action="store_true")
    sys.exit(asyncio.run(main(parser.parse_args())))
