"""Run an :class:`IndicoMock` on a real socket.

MEOW reaches Indico through aiohttp, so the mock must listen on a real TCP
port. The server runs in a background thread on a random free port.
"""

import socket
import threading
import time
from pathlib import Path

import uvicorn

from tests.mock_indico.app import IndicoMock


class IndicoMockServer:
    """Context manager: ``with IndicoMockServer(dir) as srv: srv.base_url``."""

    def __init__(self, fixture_dir: Path) -> None:
        self.mock = IndicoMock(fixture_dir)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(("127.0.0.1", 0))
        self.base_url = f"http://127.0.0.1:{self._sock.getsockname()[1]}"
        # loop="asyncio": the default ("auto") would install uvloop as the
        # *global* event loop policy from the server thread, breaking the
        # subprocess support of loops created afterwards in the main thread.
        self._server = uvicorn.Server(
            uvicorn.Config(
                self.mock.app, log_level="warning", lifespan="off", loop="asyncio"
            )
        )
        self._thread = threading.Thread(
            target=self._server.run, kwargs={"sockets": [self._sock]}, daemon=True
        )

    def __enter__(self) -> "IndicoMockServer":
        self._thread.start()
        deadline = time.monotonic() + 10
        while not self._server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("Indico mock server did not start")
            time.sleep(0.01)
        return self

    def __exit__(self, *exc) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=10)
        self._sock.close()
