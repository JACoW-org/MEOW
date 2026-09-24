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

    def contribution(code, affiliations, published=True, doi=True, ris=None):
        return SimpleNamespace(
            code=code,
            title=code,
            is_slides_included=False,
            is_posters_included=False,
            is_included_in_prepress=False,
            is_included_in_proceedings=published,
            doi_data=object() if doi else None,
            reference=SimpleNamespace(ris=ris) if ris else None,
            authors_list=[SimpleNamespace(affiliations=affiliations)] * 2,
            institutes=[institute] if "Lab" in affiliations else [other],
        )

    plugin = HugoProceedingsPlugin.__new__(HugoProceedingsPlugin)
    plugin.src_dir = Path(tmp_path)
    plugin.src_doi_per_institute_dir = Path(tmp_path, "content", "doi_per_institute")
    plugin.institutes = [institute, other]
    plugin.contributions = [
        contribution("A", {"Lab"}, ris="TY  - JOUR\nER  - "),
        contribution("B", {"Lab"}, ris="TY  - CONF\nER  - "),
        contribution("C", {"Lab"}, published=False, ris="excluded"),
        contribution("D", {"Lab"}, doi=False, ris="excluded"),
        contribution("E", {"Other"}, ris=None),
    ]
    plugin.filter_published_contributions = lambda c: True
    rendered = []

    async def render_partial(institutes, groups, ris_ids):
        rendered.extend(institutes)
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