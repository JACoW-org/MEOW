"""Optimization of the brief/volume PDFs: garbage collection, metadata and
linearization (issue JACoW-org/CAT#27)."""

import asyncio
import os
import subprocess
from pathlib import Path
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

    assert len(logs) == 2 and all("garbage=4" in m.message for m in logs)
    assert all(m.severity.value == "info" for m in logs)


def test_garbage_setting_changes_the_result(meow_workdir):
    volume = f"{EVENT_ID}_proceedings_volume.pdf"

    cache, _, _ = _run(meow_workdir, {})
    aggressive = os.path.getsize(cache / volume)

    cache, _, logs = _run(meow_workdir, {"pdf_optimize_aggressive": False})
    light = os.path.getsize(cache / volume)

    assert all("garbage=2" in m.message for m in logs)
    # level 4 merges the duplicated image streams, level 2 does not
    assert aggressive < light
    assert "File is linearized" in _qpdf_check(cache / volume).stdout


def test_optimization_failure_keeps_the_original(meow_workdir, monkeypatch):
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
    assert any("optimization failed" in m.message and m.severity.value == "warning" for m in logs)
    assert data.proceedings_volume_size == 0
    assert not list(cache.glob("*.opt.pdf"))


def test_linearization_failure_keeps_the_optimized_file(meow_workdir, monkeypatch):
    """The optimization can take a long time on big volumes: a failure of qpdf
    must not throw it away (IPAC'26 volume, qpdf 11 above 2 GiB)."""
    import meow.services.local.event.final_proceedings.optimize_proceedings_pdfs as step

    async def failing(*args, **kwargs):
        return 1

    monkeypatch.setattr(step, "pdf_linearize_final_qpdf", failing)
    cache, data, logs = _run(meow_workdir, {})

    for kind, size_attr in (("brief", "proceedings_brief_size"),
                            ("volume", "proceedings_volume_size")):
        pdf = cache / f"{EVENT_ID}_proceedings_{kind}.pdf"
        assert "File is linearized" not in _qpdf_check(pdf).stdout
        assert getattr(data, size_attr) == os.path.getsize(pdf)
        with fitz.open(pdf) as doc:
            assert "Test Conference" in doc.metadata["title"]

    assert not list(cache.glob("*.opt.pdf")) and not list(cache.glob("*.lin.pdf"))
    assert all("qpdf failed" in m.message and m.severity.value == "warning" for m in logs)


def test_the_bundled_qpdf_is_used():
    """qpdf 11 (the one in PATH on the production host) aborts on files larger
    than 2 GiB: the linearization must use the bundled qpdf 12."""
    from meow.services.local.event.final_proceedings.event_pdf_utils import get_qpdf_cmd

    out = subprocess.run([get_qpdf_cmd(), "--version"], capture_output=True, text=True).stdout
    version = tuple(int(x) for x in out.split()[2].split(".")[:2])
    assert version >= (12, 0), out


def test_slides_and_posters_are_linearized(meow_workdir, tmp_path):
    from meow.services.local.event.final_proceedings.event_pdf_utils import (
        pdf_linearize_qpdf,
    )

    src, dst = tmp_path / "talk.pdf", tmp_path / "talk_jacow"
    _merged_pdf(src, copies=3)

    assert asyncio.run(pdf_linearize_qpdf(str(src), str(dst), None, None)) == 0

    check = _qpdf_check(dst)
    assert check.returncode == 0, check.stderr
    assert "File is linearized" in check.stdout
    assert "File is linearized" not in _qpdf_check(src).stdout


def test_file_too_large_to_linearize_is_only_optimized(meow_workdir, monkeypatch):
    import meow.services.local.event.final_proceedings.optimize_proceedings_pdfs as step

    monkeypatch.setattr(step, "LINEARIZATION_MAX_BYTES", 1)
    cache, data, logs = _run(meow_workdir, {})

    for kind, size_attr in (("brief", "proceedings_brief_size"),
                            ("volume", "proceedings_volume_size")):
        pdf = cache / f"{EVENT_ID}_proceedings_{kind}.pdf"
        check = _qpdf_check(pdf)
        assert check.returncode == 0, check.stderr
        assert "File is linearized" not in check.stdout
        assert getattr(data, size_attr) == os.path.getsize(pdf)
        with fitz.open(pdf) as doc:
            assert "Test Conference" in doc.metadata["title"]

    assert not list(cache.glob("*.opt.pdf")) and not list(cache.glob("*.lin.pdf"))
    assert all("not linearized" in m.message for m in logs)


def _write_big_pdf(path, pages=3, stream_mb=800):
    """A valid PDF larger than 2 GiB (streams marked as already compressed, so qpdf
    keeps them), with a shared font and an outline: the
    objects after the page streams are the ones whose hint offsets overflow."""
    chunk = b"\0" * (1024 * 1024)
    font, outline, item = 3 + 2 * pages, 4 + 2 * pages, 5 + 2 * pages
    n_objs = item
    offsets = {}
    with open(path, "wb") as f:
        def obj(num, body):
            offsets[num] = f.tell()
            f.write(f"{num} 0 obj\n".encode() + body + b"\nendobj\n")

        f.write(b"%PDF-1.7\n")
        obj(1, f"<< /Type /Catalog /Pages 2 0 R /Outlines {outline} 0 R >>".encode())
        kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(pages))
        obj(2, f"<< /Type /Pages /Count {pages} /Kids [{kids}] >>".encode())
        for i in range(pages):
            # the font is shared by the pages after the first one only: it is
            # written after the (huge) first page part
            res = f"<< /Font << /F1 {font} 0 R >> >>" if i else "<< >>"
            obj(3 + 2 * i, (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] "
                            f"/Resources {res} /Contents {4 + 2 * i} 0 R >>").encode())
            num = 4 + 2 * i
            offsets[num] = f.tell()
            f.write(f"{num} 0 obj\n<< /Filter /JPXDecode /Length {stream_mb * len(chunk)} >>\nstream\n".encode())
            for _ in range(stream_mb):
                f.write(chunk)
            f.write(b"\nendstream\nendobj\n")
        obj(font, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        obj(outline, f"<< /Type /Outlines /Count 1 /First {item} 0 R /Last {item} 0 R >>".encode())
        obj(item, f"<< /Title (Page 1) /Parent {outline} 0 R /Dest [3 0 R /Fit] >>".encode())
        xref = f.tell()
        f.write(f"xref\n0 {n_objs + 1}\n0000000000 65535 f \n".encode())
        for num in range(1, n_objs + 1):
            f.write(f"{offsets[num]:010d} 00000 n \n".encode())
        f.write(f"trailer\n<< /Size {n_objs + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())


@pytest.mark.skipif(not os.environ.get("MEOW_TEST_LARGE_PDF"),
                    reason="needs 5 GB of disk: set MEOW_TEST_LARGE_PDF to a directory on disk (not tmpfs)")
def test_linearization_between_2_and_4_gib_is_valid(meow_workdir):
    """qpdf writes the hint offsets as unsigned 32-bit values but its check reads
    them as signed: above 2 GiB it reports mismatches that are exactly the hint
    stream length (hint + 2**32 + H_length == computed). Nothing else may be reported."""
    import re

    from meow.services.local.event.final_proceedings.event_pdf_utils import (
        pdf_linearize_final_qpdf,
    )

    big_dir = Path(os.environ["MEOW_TEST_LARGE_PDF"])
    big_dir.mkdir(parents=True, exist_ok=True)
    src, dst = big_dir / "big.pdf", big_dir / "big.lin.pdf"
    try:
        _write_big_pdf(src)
        assert src.stat().st_size > 2**31

        assert asyncio.run(pdf_linearize_final_qpdf(str(src), str(dst))) == 0
        assert dst.stat().st_size < 2**32
        check = _qpdf_check(dst)
        show = subprocess.run(["qpdf", "--show-linearization", str(dst)],
                              capture_output=True, text=True).stdout
    finally:
        src.unlink(missing_ok=True)
        dst.unlink(missing_ok=True)

    assert "File is linearized" in check.stdout
    h_length = int(re.search(r"^H_length: (\d+)", show, re.M).group(1))

    warnings = [l for l in check.stderr.splitlines() if l.startswith("WARNING")]
    assert warnings, "the overflowing offsets were expected to be reported"
    for w in warnings:
        m = re.search(r"hint table = (-?\d+); computed = (\d+)", w)
        assert m, f"unexpected warning: {w}"
        assert int(m.group(1)) + 2**32 + h_length == int(m.group(2))


def test_pikepdf_bundles_a_qpdf_with_valid_hint_tables():
    """pikepdf 8.x bundled qpdf 11.8, whose hint tables were wrong for about a
    quarter of the real papers ("object count mismatch for page N")."""
    import pikepdf

    assert tuple(int(x) for x in pikepdf.__libqpdf_version__.split(".")[:2]) >= (12, 0)
