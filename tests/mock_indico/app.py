"""Starlette app that emulates the Indico/PURR endpoints consumed by MEOW.

The mock is a *file-tree server*: a GET on ``/<path>`` is answered with the
file ``<fixture_dir>/<path>`` (or ``<fixture_dir>/<path>.json``). The layout of
a fixture therefore mirrors the URLs MEOW calls, e.g.::

    event/1/manage/purr/abstract-booklet-sessions-data.json
    event/1/manage/purr/abstract-booklet-contributions-data/11.json

Adding support for new endpoints (final proceedings, PDF downloads, ...) only
requires adding files to the fixture, not code to the mock.
"""

from dataclasses import dataclass, field
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Route

SESSION_COOKIE = "indico_session_http"


@dataclass
class RecordedRequest:
    path: str
    cookies: dict[str, str]


@dataclass
class IndicoMock:
    """Serves a fixture directory and records the requests it receives."""

    fixture_dir: Path
    requests: list[RecordedRequest] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.fixture_dir = Path(self.fixture_dir).resolve()
        self.app = Starlette(
            routes=[Route("/{path:path}", self._handle, methods=["GET"])]
        )

    @property
    def paths(self) -> list[str]:
        return [r.path for r in self.requests]

    def _resolve(self, path: str) -> Path | None:
        for candidate in (self.fixture_dir / path, self.fixture_dir / f"{path}.json"):
            candidate = candidate.resolve()
            if candidate.is_file() and candidate.is_relative_to(self.fixture_dir):
                return candidate
        return None

    async def _handle(self, request: Request) -> Response:
        path = request.path_params["path"]
        self.requests.append(RecordedRequest(f"/{path}", dict(request.cookies)))

        # Like Indico, refuse anonymous requests: this verifies that MEOW
        # forwards the session cookie it received from the plugin.
        if not request.cookies.get(SESSION_COOKIE):
            return JSONResponse({"error": True, "message": "forbidden"}, status_code=403)

        file = self._resolve(path)
        if file is None:
            return JSONResponse({"error": True, "message": "not found"}, status_code=404)

        if file.suffix == ".json":
            return Response(file.read_bytes(), media_type="application/json")
        return FileResponse(file)
