from types import SimpleNamespace

from anyio import Path, run

from meow.models.local.event.final_proceedings.event_model import AffiliationData
from meow.services.local.event.final_proceedings.hugo_plugin.hugo_final_proceedings_plugin import (
    HugoProceedingsPlugin,
)


def test_institute_ris_export(tmp_path):
    institute = AffiliationData(
        id="42", name="Lab", street="", postcode="", city="", country_code=""
    )
    other = AffiliationData(
        id="43", name="Other", street="", postcode="", city="", country_code=""
    )

    def contribution(code, institutes, published=True, doi=True, ris=None):
        return SimpleNamespace(
            code=code,
            title=code,
            is_slides_included=False,
            is_posters_included=False,
            is_included_in_prepress=False,
            is_included_in_proceedings=published,
            doi_data=object() if doi else None,
            reference=SimpleNamespace(ris=ris) if ris else None,
            # author affiliations deliberately differ from contribution institutes:
            # the RIS export must follow the same grouping as the DOI list
            authors_list=[SimpleNamespace(affiliations={"Unrelated"})],
            institutes=institutes,
        )

    plugin = HugoProceedingsPlugin.__new__(HugoProceedingsPlugin)
    plugin.src_dir = Path(tmp_path)
    plugin.src_doi_per_institute_dir = Path(tmp_path, "content", "doi_per_institute")
    plugin.institutes = [institute, other]
    plugin.contributions = [
        contribution("A", [institute], ris="TY  - JOUR\nER  - "),
        contribution("B", [institute], ris="TY  - CONF\nER  - "),
        contribution("C", [institute], published=False, ris="excluded"),
        contribution("D", [institute], doi=False, ris="excluded"),
        contribution("E", [other], ris=None),
    ]
    plugin.filter_published_contributions = lambda c: c.is_included_in_proceedings
    rendered = []

    async def render_partial(institutes, groups, ris_ids):
        rendered.extend(institutes)
        assert [c["code"] for c in groups["Lab"]] == ["A", "B"]
        assert [c["code"] for c in groups["Other"]] == ["E"]
        assert ris_ids == {"42"}
        return "partial"

    async def render_page(event, institute, contribution):
        return "page"

    plugin.template = SimpleNamespace(
        render_doi_per_institute_partial=render_partial,
        render_doi_per_institute_page=render_page,
    )
    plugin.event = None

    async def check():
        await Path(tmp_path, "layouts", "partials", "doi_per_institute").mkdir(
            parents=True
        )
        await plugin.src_doi_per_institute_dir.mkdir(parents=True)
        await plugin.render_doi_per_institute()
        assert await Path(tmp_path, "static", "ris", "institute", "42.ris").read_text() == (
            "TY  - JOUR\nER  -\n\nTY  - CONF\nER  -\n"
        )
        assert not await Path(tmp_path, "static", "ris", "institute", "43.ris").exists()
        assert rendered == [institute, other]

    run(check)