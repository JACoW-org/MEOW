"""Citation metadata (Highwire Press / Dublin Core) of the DOI landing pages (CAT#37)."""

import asyncio
import re
import shutil
import subprocess
import tomllib
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import pytest

import meow.services.local.event.final_proceedings.hugo_plugin.hugo_jinja_template_renderer as renderer_module
from meow.models.local.event.final_proceedings.event_model import EventData
from meow.tasks.local.doi.models import AuthorDOI, ContributionDOI
from meow.utils.escape import toml_string

REPO_ROOT = Path(__file__).resolve().parents[1]

TITLE = 'Machine "learning" <b>driven</b> \\beta-function & $\\alpha$ \U0001d465 reconstruction'
ABSTRACT = 'The "LANSCE" relies on <accurate> tuning.\nSecond line with """ and a \\ backslash.'


@pytest.fixture(autouse=True)
def project_root(monkeypatch):
    # templates and binaries are resolved relative to the project root
    monkeypatch.chdir(REPO_ROOT)
    # do not write the Jinja bytecode cache under var/
    monkeypatch.setattr(renderer_module, "FileSystemCache", lambda directory: None)


def make_contribution(**overrides) -> ContributionDOI:
    values = dict(
        code="THPM024",
        title=TITLE,
        timezone="UTC",
        primary_authors=[
            AuthorDOI(id="1", first_name="Petr", last_name="Anisimov"),
            AuthorDOI(id="2", first_name="", last_name="Scheinker"),
            AuthorDOI(id="3", first_name="Eric", last_name="Huang"),
        ],
        abstract=ABSTRACT,
        keywords=["electron", "linac"],
        conference_code="16th International Particle Accelerator Conference",
        venue="Taipei, Taiwan",
        date="1-6 Jun 2025",
        conference_doi_name="IPAC2025",
        isbn="978-3-95450-248-6",
        issn="2673-5490",
        issuance_date_iso="2025-11-05",
        doi_name="10.18429/JACoW-IPAC2025-THPM024",
        doi_path="jacow-ipac2025-thpm024",
        pages="2733-2736",
    )
    values.update(overrides)
    return ContributionDOI(**values)


def make_event() -> EventData:
    return EventData(
        id="1", name="IPAC2025", title="IPAC'25", hosted="", timezone="UTC",
        editorial="", location="Taipei", date="", isbn="", issn="", color="#000",
        series="", series_number="", copyright_year="2025", site_license_text="",
        site_license_url="", paper_license_icon_url="", paper_license_text="",
        doi_url="", doi_label="", start=datetime(2025, 6, 1), end=datetime(2025, 6, 6),
    )


def render_page(contribution: ContributionDOI) -> str:
    renderer = renderer_module.JinjaTemplateRenderer()
    return asyncio.run(renderer.render_doi_contribution(contribution))


def render_partial(contribution: ContributionDOI) -> str:
    renderer = renderer_module.JinjaTemplateRenderer()
    return asyncio.run(renderer.render_doi_partial(make_event(), contribution))


def front_matter(page: str) -> dict:
    assert page.startswith("+++\n") and page.rstrip().endswith("+++")
    return tomllib.loads(page.removeprefix("+++\n").rstrip().removesuffix("+++"))


# toml_string -----------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ['plain', 'say "hi"', "back\\slash", "two\nlines", "tab\tand\x7fDEL", "\U0001d465 non-BMP", '"""', "", None],
)
def test_toml_string_round_trips(value):
    assert tomllib.loads(f"v = {toml_string(value)}")["v"] == ("" if value is None else value)


# front matter ----------------------------------------------------------------


def test_front_matter_is_valid_toml_and_keeps_special_characters():
    meta = front_matter(render_page(make_contribution()))

    assert meta["type"] == "doi"
    assert meta["title"] == TITLE
    assert meta["cit_title"] == TITLE
    # whitespace (including the newline) is collapsed, nothing else changes
    assert meta["cit_abstract"] == " ".join(ABSTRACT.split())
    assert meta["contents"] == ["contributions/thpm024_doi.html"]


def test_front_matter_citation_fields():
    meta = front_matter(render_page(make_contribution()))

    assert meta["cit_authors"] == ["Anisimov, Petr", "Scheinker", "Huang, Eric"]
    assert meta["cit_keywords"] == ["electron", "linac"]
    assert meta["cit_publication_date"] == "2025/11/05"
    assert meta["cit_firstpage"] == "2733"
    assert meta["cit_lastpage"] == "2736"
    assert meta["cit_doi"] == "10.18429/JACoW-IPAC2025-THPM024"
    assert meta["cit_isbn"] == "978-3-95450-248-6"
    assert meta["cit_issn"] == "2673-5490"
    assert meta["cit_journal_title"] == "Proceedings of IPAC2025"
    assert meta["cit_publisher"] == "JACoW Publishing, Geneva, Switzerland"
    assert meta["cit_conference_title"] == (
        "16th International Particle Accelerator Conference, Taipei, Taiwan, 1-6 Jun 2025"
    )
    assert meta["cit_language"] == "en"
    assert meta["cit_pdf_url"] == "https://jacow.org/ipac2025/pdf/THPM024.pdf"


def test_front_matter_omits_unavailable_values():
    meta = front_matter(
        render_page(
            make_contribution(
                title="", issn="0000-0000", isbn="", pages="", issuance_date_iso="",
                keywords=[], abstract="", primary_authors=[],
            )
        )
    )

    assert meta["title"] == "THPM024"  # falls back to the code
    assert meta["cit_authors"] == []
    assert meta["cit_keywords"] == []
    for key in ("cit_issn", "cit_isbn", "cit_firstpage", "cit_lastpage", "cit_publication_date", "cit_abstract"):
        assert meta[key] == ""


# landing page partial ---------------------------------------------------------


def test_pdf_link_is_a_plain_crawlable_link():
    html = render_partial(make_contribution())

    # the partial is minified, so attribute quotes may be omitted
    assert re.search(r'<a [^>]*href="?\.\./\.\./pdf/THPM024\.pdf"?[ >]', html)
    # no JavaScript openUrl()/data-href for the PDF
    assert "openUrl(`pdf/" not in html and "data-href=pdf/" not in html


def test_pdf_url_property_matches_inspire_document_url():
    contribution = make_contribution()

    assert contribution.pdf_url == "https://jacow.org/ipac2025/pdf/THPM024.pdf"
    assert contribution._build_hep_attributes()["documents"][0]["url"] == contribution.pdf_url


# generated HTML (real Hugo build) ------------------------------------------------


class _Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.metas: list[tuple[str, str]] = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "name" in attrs:
            self.metas.append((attrs["name"], attrs.get("content", "")))
        self._in_title = tag == "title"

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def _hugo_available() -> bool:
    hugo = REPO_ROOT / "bin" / "hugo"
    try:
        return subprocess.run([str(hugo), "version"], capture_output=True).returncode == 0
    except OSError:
        return False


@pytest.mark.skipif(not _hugo_available(), reason="bin/hugo is not runnable here")
def test_hugo_site_emits_citation_metadata(tmp_path):
    contribution = make_contribution()
    site = tmp_path / "site"
    shutil.copytree(REPO_ROOT / "assets" / "hugo_tpl", site)
    (site / "config.toml").write_text(
        'baseURL = "/ipac2025/"\ntitle = "IPAC2025"\n'
        'disableKinds = ["RSS", "taxonomy", "taxonomyTerm", "sitemap", "robotsTXT"]\n'
        '[params]\ncolor = "#000"\n'
    )
    (site / "content" / "doi").mkdir(parents=True)
    (site / "content" / "doi" / "jacow-ipac2025-thpm024.html").write_text(render_page(contribution))
    (site / "layouts" / "partials" / "contributions").mkdir(parents=True)
    (site / "layouts" / "partials" / "contributions" / "thpm024_doi.html").write_text(render_partial(contribution))

    result = subprocess.run(
        [str(REPO_ROOT / "bin" / "hugo"), "--source", str(site), "--destination", str(site / "out")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    parser = _Head()
    parser.feed((site / "out" / "doi" / "jacow-ipac2025-thpm024" / "index.html").read_text())
    metas = parser.metas

    def values(name):
        return [content for key, content in metas if key == name]

    # the contribution title (not the code) is the HTML title, HTML characters are escaped
    assert parser.title.strip() == TITLE
    assert values("citation_title") == [TITLE]
    assert values("citation_author") == ["Anisimov, Petr", "Scheinker", "Huang, Eric"]
    assert values("DC.creator") == values("citation_author")
    assert values("citation_publication_date") == ["2025/11/05"]
    assert values("citation_doi") == ["10.18429/JACoW-IPAC2025-THPM024"]
    assert values("citation_firstpage") == ["2733"]
    assert values("citation_lastpage") == ["2736"]
    assert values("citation_pdf_url") == ["https://jacow.org/ipac2025/pdf/THPM024.pdf"]
    assert values("citation_keywords") == ["electron, linac"]
    assert values("DC.identifier") == [
        "info:doi/10.18429/JACoW-IPAC2025-THPM024",
        "https://jacow.org/ipac2025/pdf/THPM024.pdf",
    ]
    assert values("dcterms:isPartOf") == ["urn:ISSN:2673-5490", "urn:ISBN:978-3-95450-248-6"]
