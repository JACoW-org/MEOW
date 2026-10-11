import json
from pathlib import Path

import pytest

from tests.mock_indico.server import IndicoMockServer

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "indico"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def indico_mock():
    """Indico/PURR mock serving the ``minimal`` fixture."""
    with IndicoMockServer(FIXTURES_DIR / "minimal") as server:
        yield server


@pytest.fixture
def task_params(indico_mock):
    """``params`` as the Indico plugin sends them to a MEOW task.

    ``event.url`` is pointed to the mock; the cookie is accepted by it.
    """
    data = json.loads((indico_mock.mock.fixture_dir / "event.json").read_text())
    data["event"]["url"] = f"{indico_mock.base_url}/event/{data['event']['id']}/"
    data["cookies"] = {"indico_session_http": "test-session"}
    return data
