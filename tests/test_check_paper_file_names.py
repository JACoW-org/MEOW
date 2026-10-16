"""Warning for papers not named after the contribution code (JACoW-org/MEOW#37)."""

from types import SimpleNamespace

import pytest

from meow.services.local.event.final_proceedings.check_paper_file_names import (
    check_paper_file_names,
)

pytestmark = pytest.mark.anyio


def contribution(code: str, paper: str | None, published: bool = True):
    return SimpleNamespace(code=code, paper_name=lambda: paper, published=published)


def proceedings(*contributions):
    return SimpleNamespace(contributions=list(contributions))


def published(c) -> bool:
    return c.published


async def test_paper_named_after_the_code_is_not_reported():
    data = proceedings(contribution("MOP001", "MOP001.pdf"))

    assert await check_paper_file_names(data, published) == []


async def test_case_and_spaces_are_ignored():
    data = proceedings(contribution(" mop001 ", "MOP001.PDF"))

    assert await check_paper_file_names(data, published) == []


async def test_paper_named_after_an_old_code_is_reported():
    data = proceedings(
        contribution("WEP5601", "THP5647.pdf"),
        contribution("WEP5602", "WEP5602.pdf"),
    )

    [warning] = await check_paper_file_names(data, published)

    assert "WEP5601" in warning
    assert "THP5647.pdf" in warning


async def test_contributions_not_published_or_without_paper_are_ignored():
    data = proceedings(
        contribution("WEP5601", "THP5647.pdf", published=False),
        contribution("WEP5603", None),
    )

    assert await check_paper_file_names(data, published) == []
