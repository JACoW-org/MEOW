"""Warning for sessions without a code (JACoW-org/MEOW#39)."""

from types import SimpleNamespace

import pytest

from meow.services.local.event.final_proceedings.check_sessions_without_code import (
    check_sessions_without_code,
)

pytestmark = pytest.mark.anyio


def session(id: int, code: str, title: str = "Session"):
    return SimpleNamespace(id=id, code=code, title=title)


def contribution(code: str, session_id: int):
    return SimpleNamespace(code=code, session_id=session_id)


def proceedings(sessions, contributions):
    return SimpleNamespace(sessions=sessions, contributions=contributions)


async def test_sessions_with_a_code_are_not_reported():
    data = proceedings([session(1, "MOA")], [contribution("MOA01", 1)])

    assert await check_sessions_without_code(data) == []


async def test_session_without_code_is_reported_with_its_contributions():
    data = proceedings(
        [session(1, "MOA"), session(64, "", "MC2 : Photon Sources")],
        [
            contribution("MOA01", 1),
            contribution("THO2M02", 64),
            contribution("THI2M01", 64),
        ],
    )

    [warning] = await check_sessions_without_code(data)

    assert "64" in warning
    assert "MC2 : Photon Sources" in warning
    assert warning.endswith(": THI2M01, THO2M02.")


async def test_session_without_code_and_without_contributions_is_ignored():
    data = proceedings([session(84, "", "Welcome")], [contribution("MOA01", 1)])

    assert await check_sessions_without_code(data) == []
