import json
import os
from pathlib import Path

import pytest

from tests.mock_indico.server import IndicoMockServer

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "indico"

# Directory of a full snapshot made with tools/snapshot_indico.py. Not versioned
# (it contains personal data and unpublished papers): tests using it are skipped
# when the variable is not set.
SNAPSHOT_ENV = "MEOW_INDICO_SNAPSHOT"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def build_task_params(server: IndicoMockServer) -> dict:
    """``params`` as the Indico plugin sends them to a MEOW task.

    Read from the ``settings-and-event-data`` endpoint of the fixture, with the
    Indico host replaced by the mock's address; the cookie is accepted by it.
    """
    mock = server.mock
    [path] = mock.fixture_dir.glob("event/*/manage/purr/settings-and-event-data.json")
    body = mock.rewrite(path.read_bytes(), server.base_url)
    data = json.loads(body)
    return dict(
        event=data["event"],
        settings=data["settings"],
        cookies={"indico_session_http": "test-session"},
    )


@pytest.fixture
def indico_mock():
    """Indico/PURR mock serving the ``minimal`` fixture."""
    with IndicoMockServer(FIXTURES_DIR / "minimal") as server:
        yield server


@pytest.fixture
def task_params(indico_mock):
    return build_task_params(indico_mock)


@pytest.fixture
def snapshot_mock():
    """Indico/PURR mock serving the snapshot in ``$MEOW_INDICO_SNAPSHOT``."""
    snapshot = os.environ.get(SNAPSHOT_ENV)
    if not snapshot:
        pytest.skip(f"{SNAPSHOT_ENV} not set")
    with IndicoMockServer(Path(snapshot)) as server:
        yield server


@pytest.fixture
def snapshot_task_params(snapshot_mock):
    return build_task_params(snapshot_mock)
