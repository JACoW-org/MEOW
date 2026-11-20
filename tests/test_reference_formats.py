"""RIS and EndNote exports (JACoW-org/CAT#44, JACoW-org/CAT#45).

The reference XML is rendered with the real template and transformed with the
real stylesheets.
"""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import Environment, FileSystemLoader
from lxml import etree

ROOT = Path(__file__).parent.parent


def person(first: str, last: str):
    return SimpleNamespace(first=first, last=last)


def context(**overrides) -> dict:
    ctx = dict(
        publisher="JACoW Publishing",
        publisher_venue="Geneva, Switzerland",
        language="English",
        conference_code="ipac2025",
        booktitle_short="IPAC'25",
        booktitle_long="16th International Particle Accelerator Conference",
        series="",
        series_number="",
        venue="Taipei, Taiwan",
        start_date="2025-06-01",
        end_date="2025-06-06",
        year="2025",
        month="June",
        issn="0000-0000",
        isbn="978-3-95450-247-6",
        status="in_proceedings",
        paper_code="MOPM001",
        authors_list=[person("Jane", "Doe")],
        editors=[],
        title="A title",
        abstract="An abstract",
        start_page=1,
        number_of_pages=3,
        url="https://jacow.org/ipac2025/pdf/MOPM001.pdf",
        doi="10.18429/JACoW-IPAC2025-MOPM001",
        keywords=[],
    )
    ctx.update(overrides)
    return ctx


def transform(stylesheet: str, **overrides) -> str:
    env = Environment(loader=FileSystemLoader(ROOT / "jinja" / "reference"), autoescape=True)
    xml = env.get_template("reference.xml.jinja").render(**context(**overrides))
    doc = etree.fromstring(xml.encode(), parser=etree.XMLParser(encoding="utf-8", recover=True))
    xslt = etree.XSLT(etree.parse(str(ROOT / "xslt" / stylesheet)))
    return str(xslt(doc))


def ris(**overrides) -> list[str]:
    return transform("ris.xml", **overrides).splitlines()


def tags(lines: list[str]) -> list[str]:
    return [line[:2] for line in lines if re.match(r"^[A-Z][A-Z0-9] +- ", line)]


# --- RIS (CAT#44) ---


def test_ris_has_two_spaces_before_the_hyphen_in_every_tag():
    lines = ris(
        editors=[person("Ed", "Itor")],
        keywords=["linac"],
        series="Series",
        series_number="3",
    )

    tag_lines = [line for line in lines if line.strip()]
    assert tag_lines and all(re.match(r"^[A-Z][A-Z0-9]  - ", line) for line in tag_lines)
    assert lines[0] == "TY  - CONF"
    assert lines[-1] == "ER  - "


def test_ris_j2_is_the_proceedings_title():
    assert "J2  - Proc. IPAC'25" in ris()


def test_ris_j2_keeps_the_previous_text_without_a_short_title():
    [j2] = [line for line in ris(booktitle_short="") if line.startswith("J2")]

    assert j2.startswith("J2  - Proc. of ipac2025, Taipei, Taiwan, 01-06 June 2025")


def test_ris_has_no_empty_ed_kw_t2_t3_lines():
    lines = ris(
        series="",
        series_number="",
        keywords=["", "  "],
        editors=[person("", "")],
    )

    assert not {"ED", "KW", "T2", "T3"} & set(tags(lines))
    assert not [line for line in lines if re.match(r"^(ED|KW|T2|T3) +- *$", line)]


def test_ris_writes_series_keywords_and_editors_when_there_are_any():
    lines = ris(
        series="JACoW Conference Series",
        series_number="7",
        keywords=["linac", "beam"],
        editors=[person("Ed", "Itor")],
    )

    assert "T2  - JACoW Conference Series" in lines
    assert "T3  - 7" in lines
    assert [line for line in lines if line.startswith("KW")] == ["KW  - linac", "KW  - beam"]
    assert "ED  - Itor, E." in lines


def test_ris_unpublished_contribution_is_unpublished_work():
    assert ris(status="not_in_proceedings")[0] == "TY  - UNPB"


# --- EndNote (CAT#45) ---


def endnote(**overrides) -> etree._Element:
    return etree.fromstring(transform("endnote.xml", **overrides).encode())


def test_endnote_has_the_reference_type_first_in_the_record():
    record = endnote().find("records/record")

    assert record[0].tag == "ref-type"
    assert (record[0].get("name"), record[0].text) == ("Conference Paper", "47")


def test_endnote_unpublished_contribution_is_unpublished_work():
    ref_type = endnote(status="not_in_proceedings").find("records/record/ref-type")

    assert (ref_type.get("name"), ref_type.text) == ("Unpublished Work", "34")


def test_endnote_has_the_proceedings_title():
    titles = endnote().find("records/record/titles")

    assert titles.findtext("title") == "A title"
    assert titles.findtext("secondary-title") == "Proc. IPAC'25"


def test_endnote_has_no_proceedings_title_without_a_short_title():
    titles = endnote(booktitle_short="").find("records/record/titles")

    assert titles.find("secondary-title") is None
