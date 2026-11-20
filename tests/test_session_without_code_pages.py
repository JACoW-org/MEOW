"""Sessions without a code are published under their id only (JACoW-org/MEOW#39)."""

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from jinja2 import Environment, FileSystemLoader

from meow.models.local.event.final_proceedings.contribution_model import (
    DuplicateContributionData,
)
from meow.models.local.event.final_proceedings.session_model import (
    SessionData,
    session_page_name,
)
from meow.services.local.event.abstract_booklet.export_abstract_booklet import (
    without_empty_code,
)
from meow.services.local.event.final_proceedings import concat_contribution_papers
from meow.services.local.event.final_proceedings.write_metadata_utils import (
    get_footer_data,
)

JINJA_DIR = Path(__file__).parent.parent / "jinja" / "final_proceedings"


def make_session(id: int, code: str, title: str = "MC2 : Photon Sources") -> SessionData:
    now = datetime(2026, 5, 19, 9, 0)
    return SessionData(
        id=id, code=code, title=title, url="", is_poster=False, start=now, end=now
    )


def render(template: str, **context) -> str:
    env = Environment(loader=FileSystemLoader(JINJA_DIR))
    return env.get_template(template).render(**context)


def test_page_name_has_the_code_when_there_is_one():
    assert session_page_name(62, "TU2") == "62-tu2"
    assert make_session(62, "TU2").page_name == "62-tu2"


def test_page_name_is_the_id_only_without_code():
    assert session_page_name(64, "") == "64"
    assert session_page_name(64, None) == "64"
    assert make_session(64, "").page_name == "64"


def test_session_list_links_a_session_without_code():
    html = render(
        "session_partial.html.jinja",
        sessions=[make_session(62, "TU2"), make_session(64, "")],
    )

    assert "session/62-tu2/index.html" in html
    assert "session/64/index.html" in html
    assert "session/64-/" not in html
    assert "<b></b>" not in html


def test_session_page_without_code_has_no_empty_name():
    html = render(
        "session_page.html.jinja",
        session=make_session(64, ""),
        contributions=[SimpleNamespace(code="THI2M01")],
    )

    assert 'name: ""' not in html
    assert "contributions/thi2m01.html" in html


def test_duplicate_link_points_to_the_session_page_without_code():
    duplicate = DuplicateContributionData(code="THI2M01", session_id=64, session_code="")

    assert duplicate.session_page_name == "64"


def test_footer_has_the_title_only_without_session_code():
    contribution = SimpleNamespace(code="THI2M01", track=None)

    footer = get_footer_data(contribution, make_session(64, ""))
    assert footer["sessionHeader"] == "MC2 : Photon Sources"

    footer = get_footer_data(contribution, make_session(62, "TU2", "Photon"))
    assert footer["sessionHeader"] == "TU2: Photon"


def test_booklet_header_drops_the_empty_code_and_its_separator():
    assert without_empty_code("{code} - {title}", "") == "{title}"
    assert without_empty_code("{code}: {title}", None) == "{title}"
    assert without_empty_code("{code} - {title}", "TU2") == "{code} - {title}"


@pytest.mark.anyio
async def test_toc_lists_the_contributions_of_a_session_without_code(
    tmp_path, monkeypatch
):
    async def vol_toc_pdf(*_):
        return 0

    monkeypatch.setattr(concat_contribution_papers, "vol_toc_pdf", vol_toc_pdf)

    def contribution(code: str, session_id: int, session_code: str, page: int):
        return SimpleNamespace(
            code=code,
            title=code,
            session_id=session_id,
            session_code=session_code,
            page=page,
        )

    event = SimpleNamespace(
        id=3, name="", title="", series="", isbn="", doi_label="", issn=""
    )
    data = SimpleNamespace(
        event=event,
        sessions=[make_session(62, "TU2"), make_session(64, "")],
        contributions=[
            contribution("TUO2M01", 62, "TU2", 1),
            contribution("THI2M01", 64, "", 5),
        ],
    )

    await concat_contribution_papers.get_vol_toc_pdf_path(
        data, None, tmp_path, lambda c: True, ["session", "contribution"]
    )

    conf = json.loads((tmp_path / "3_proceedings_volume_toc.conf.json").read_text())
    items = [(i["type"], i.get("code") or i["title"]) for i in conf["toc_items"]]

    assert ("contribution", "THI2M01") in items
    assert ("session", "MC2 : Photon Sources") in items
