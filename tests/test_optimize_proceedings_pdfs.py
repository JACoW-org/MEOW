"""Optimization of the brief/volume PDFs: garbage collection, metadata and
linearization (issue JACoW-org/CAT#27)."""

import asyncio
import os
import subprocess
from types import SimpleNamespace

import fitz
import pytest

from meow.services.local.event.final_proceedings.optimize_proceedings_pdfs import (
    get_garbage_level,
    optimize_proceedings_pdfs,
)

EVENT_ID = 7


def _merged_pdf(path, copies=6):
    """A PDF made of `copies` copies of a page with an image: the merge keeps
    one copy of the image per page, which only garbage level 4 can merge."""
    src = fitz.open()
    page = src.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 200, 200), False)
    pix.set_rect(pix.irect, (10, 120, 200))
    page.insert_image(page.rect, pixmap=pix)
    page.insert_text((72, 72), "paper")
    src_bytes = src.tobytes()

    doc = fitz.open()
    for _ in range(copies):
        with fitz.open("pdf", src_bytes) as part:
            doc.insert_pdf(part)
    doc.save(str(path), garbage=0, deflate=False)


def _proceedings():
    return SimpleNamespace(
        event=SimpleNamespace(id=EVENT_ID, title="Test Conference"),
        proceedings_brief_size=0,
        proceedings_volume_size=0,
    )


def _run(meow_workdir, settings, copies=6):
    cache = meow_workdir / "var" / "run" / f"{EVENT_ID}_tmp"
    cache.mkdir(parents=True, exist_ok=True)
    for kind in ("brief", "volume"):
        _merged_pdf(cache / f"{EVENT_ID}_proceedings_{kind}.pdf", copies)

    data, logs = asyncio.run(
        optimize_proceedings_pdfs(_proceedings(), {}, settings, SimpleNamespace(), lambda: None)
    )
    return cache, data, logs


def _qpdf_check(path):
    return subprocess.run(
        ["qpdf", "--check", str(path)], capture_output=True, text=True
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, 4), ("", 4), (True, 4), ("true", 4), ("1", 4), (1, 4),
        (False, 2), ("false", 2), ("False", 2), ("0", 2), (0, 2), ("off", 2),
    ],
)
def test_garbage_level(value, expected):
    settings = {} if value is None else {"pdf_optimize_aggressive": value}
    assert get_garbage_level(settings) == expected


def test_optimize_is_valid_linearized_and_keeps_metadata(meow_workdir):
    cache, data, logs = _run(meow_workdir, {})

    for kind, size_attr in (("brief", "proceedings_brief_size"),
                            ("volume", "proceedings_volume_size")):
        pdf = cache / f"{EVENT_ID}_proceedings_{kind}.pdf"
        check = _qpdf_check(pdf)

        # qpdf reports an invalid linearization (hint tables) as a warning
        assert check.returncode == 0, check.stderr
        assert "File is linearized" in check.stdout
        assert "linearization data" not in check.stderr

        assert getattr(data, size_attr) == os.path.getsize(pdf)

        with fitz.open(pdf) as doc:
            assert doc.page_count == 6
            assert "Test Conference" in doc.metadata["title"]
            assert doc.metadata["producer"] == "JACoW Conference Assembly Tool (CAT)"
            assert b"Test Conference" in doc.get_xml_metadata().encode()

        assert not list(cache.glob("*.opt.pdf")) and not list(cache.glob("*.lin.pdf"))

    assert len(logs) == 2 and all("garbage=4" in m for m in logs)


def test_garbage_setting_changes_the_result(meow_workdir):
    volume = f"{EVENT_ID}_proceedings_volume.pdf"

    cache, _, _ = _run(meow_workdir, {})
    aggressive = os.path.getsize(cache / volume)

    cache, _, logs = _run(meow_workdir, {"pdf_optimize_aggressive": False})
    light = os.path.getsize(cache / volume)

    assert all("garbage=2" in m for m in logs)
    # level 4 merges the duplicated image streams, level 2 does not
    assert aggressive < light
    assert "File is linearized" in _qpdf_check(cache / volume).stdout


def test_failure_keeps_the_original_and_suggests_a_retry(meow_workdir, monkeypatch):
    import meow.services.local.event.final_proceedings.optimize_proceedings_pdfs as step

    async def failing(*args, **kwargs):
        return 1

    monkeypatch.setattr(step, "pdf_optimize_with_metadata", failing)
    cache = meow_workdir / "var" / "run" / f"{EVENT_ID}_tmp"
    cache.mkdir(parents=True)
    pdf = cache / f"{EVENT_ID}_proceedings_volume.pdf"
    _merged_pdf(pdf)
    before = pdf.read_bytes()

    data, logs = asyncio.run(
        step.optimize_proceedings_pdfs(_proceedings(), {}, {}, SimpleNamespace(), lambda: None)
    )

    assert pdf.read_bytes() == before
    assert any("pdf_optimize_aggressive" in m for m in logs)
    assert data.proceedings_volume_size == 0
