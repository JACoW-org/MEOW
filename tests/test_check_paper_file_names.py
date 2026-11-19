"""Warning for papers not named after the contribution code (JACoW-org/MEOW#37)."""

from types import SimpleNamespace

import pytest

from meow.services.local.event.final_proceedings.check_paper_file_names import (
    check_paper_file_names,
)

pytestmark = pytest.mark.anyio


def contribution(code: str, paper: str | None, published: bool = True):
    return SimpleNamespace(
        code=code, paper_original_name=lambda: paper, published=published
    )


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


# --- the paper is named after the contribution code in the site (option A) ---

from meow.models.local.event.final_proceedings.contribution_factory import (
    name_papers_after_code,
)
from meow.models.local.event.final_proceedings.contribution_model import (
    EditableData,
    FileData,
    RevisionData,
)


def make_file(filename: str, file_type: int = FileData.FileType.paper) -> FileData:
    return FileData(
        file_type=file_type,
        content_type="application/pdf",
        download_url="",
        external_download_url="",
        filename=filename,
        md5sum="",
        uuid=filename,
    )


def test_paper_file_is_named_after_the_code_keeping_the_uploaded_name():
    paper = make_file("THP5647.pdf")
    slides = make_file("THP5647_talk.pdf", FileData.FileType.slides)
    revision = RevisionData.__new__(RevisionData)
    revision.files = [paper, slides]
    editable = EditableData.__new__(EditableData)
    editable.all_revisions = [revision]
    editable.latest_revision = revision

    name_papers_after_code(editable, "WEP5601")

    assert paper.filename == "WEP5601.pdf"
    assert paper.original_filename == "THP5647.pdf"
    assert slides.filename == "THP5647_talk.pdf"


def test_name_papers_after_code_ignores_missing_editable():
    name_papers_after_code(None, "WEP5601")
