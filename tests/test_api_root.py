"""GET /api/ answers instead of failing with a 500."""

import json

import pytest
from starlette.applications import Starlette
from starlette.routing import Mount

from meow.routes.api import routes as api_routes

pytestmark = pytest.mark.anyio


async def call(method: str, path: str) -> tuple[int, bytes]:
    """Call the ASGI application directly (no HTTP client dependency)."""
    app = Starlette(routes=[Mount("/api", routes=api_routes)])
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "scheme": "http",
        "server": ("test", 80),
        "client": ("test", 1),
    }
    sent: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    await app(scope, receive, send)
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return status, body


async def test_api_root_answers():
    status, body = await call("GET", "/api/")

    assert status == 200
    assert json.loads(body) == {"method": "root"}


async def test_api_root_answers_to_options():
    status, _ = await call("OPTIONS", "/api/")

    assert status == 200
