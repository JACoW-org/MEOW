"""Institutes of a contribution (CAT#41, CAT#42).

PURR serialises the institutes of the primary authors only, and the free text
of their affiliation as it is ("A; B" for an author with two affiliations).
"""

from meow.models.local.event.final_proceedings.contribution_factory import (
    contribution_institutes_factory,
)
from meow.models.local.event.final_proceedings.event_model import PersonData


def person(*affiliations: str) -> PersonData:
    return PersonData(
        id="-".join(affiliations) or "none",
        first="A",
        last="B",
        affiliations=set(affiliations),
        email="",
    )


def names(institutes) -> list[str]:
    return sorted(i.name for i in institutes)


def test_institute_of_a_coauthor_is_listed():
    # CAT#41: the institute of a coauthor was not in the list
    institutes = contribution_institutes_factory(
        [{"name": "JLab"}], [person("JLab"), person("SAES Getters S.p.A.")]
    )

    assert names(institutes) == ["JLab", "SAES Getters S.p.A."]


def test_double_affiliation_is_split():
    # CAT#42: "A; B" was listed as an institute without authors
    institutes = contribution_institutes_factory(
        [{"name": "Cockcroft Institute"}, {"name": "Daresbury Laboratory; Cockcroft Institute"}],
        [person("Daresbury Laboratory", "Cockcroft Institute")],
    )

    assert names(institutes) == ["Cockcroft Institute", "Daresbury Laboratory"]


def test_institute_data_from_indico_is_kept():
    institutes = contribution_institutes_factory(
        [{"name": "CERN", "city": "Meyrin", "country_code": "CH"}], [person("CERN")]
    )

    [cern] = institutes
    assert cern.city == "Meyrin"
    assert cern.country_code == "CH"


def test_empty_and_duplicate_names_are_ignored():
    institutes = contribution_institutes_factory(
        [{"name": " CERN "}, {"name": ""}, {"name": "CERN"}], [person("CERN"), person()]
    )

    assert names(institutes) == ["CERN"]


# --- authors are matched to an institute by id (slug), not by exact name ---

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from meow.models.local.event.final_proceedings.event_model import AffiliationData
from meow.utils.collections import (
    authors_of_institute,
    group_authors_by_institute,
    group_institutes_by_initial,
)
from meow.utils.slug import slugify


def institute(name: str) -> AffiliationData:
    return AffiliationData(
        id=slugify(name), name=name, street=None, postcode=None, city=None,
        country_code=None,
    )


def test_authors_with_different_spellings_of_an_institute_are_grouped_together():
    # CAT#41: "SAES Getters S.p.A" and "SAES Getters S.p.A." are one institute
    a, b = person("SAES Getters S.p.A."), person("SAES Getters S.p.A")
    b.id = "other"

    groups = group_authors_by_institute([a, b])

    assert list(groups) == [slugify("SAES Getters S.p.A.")]
    assert [x["code"] for x in groups[slugify("SAES Getters S.p.A")]] == [a.code, b.code]


def test_author_with_two_spellings_of_the_same_institute_is_listed_once():
    a = person("Fusion For Energy", "Fusion for Energy")

    [group] = group_authors_by_institute([a]).values()

    assert [x["code"] for x in group] == [a.code]


def test_authors_of_an_institute_are_found_by_id_whatever_the_spelling():
    a, b, c = person("Synchrotron Soleil"), person("Synchrotron SOLEIL"), person("CERN")
    b.id, c.id = "b", "c"

    found = authors_of_institute([a, b, c], institute("Synchrotron Soleil").id)

    assert found == [a, b]


def test_institute_list_shows_the_authors_of_every_spelling():
    a, b = person("SAES Getters S.p.A."), person("SAES Getters S.p.A")
    b.id = "other"
    institutes = [institute("SAES Getters S.p.A.")]
    jinja = Environment(
        loader=FileSystemLoader(Path(__file__).parent.parent / "jinja" / "final_proceedings")
    )

    html = jinja.get_template("institute_partial.html.jinja").render(
        authorsGroups=group_authors_by_institute([a, b]),
        institutes_groups=group_institutes_by_initial(institutes),
        initials={"s": True},
    )

    assert html.count('<li class="author">') == 2


# --- institutes no author uses are not listed (CAT#43, follow-up of CAT#42) ---


def test_free_text_different_from_the_linked_affiliation_is_not_an_institute():
    # PURR sends the linked name ("Institute") and the free text ("Institut"):
    # authors use the linked one, the free text would be an institute without authors
    institutes = contribution_institutes_factory(
        [{"name": "Paul Scherrer Institute"}, {"name": "Paul Scherrer Institut"}],
        [person("Paul Scherrer Institute")],
    )

    assert names(institutes) == ["Paul Scherrer Institute"]


def test_generic_free_text_is_not_an_institute_when_authors_use_the_linked_ones():
    institutes = contribution_institutes_factory(
        [
            {"name": "INFN, Laboratori Nazionali di Legnaro"},
            {"name": "Facility for Rare Isotope Beams"},
            {"name": "Istituto Nazionale di Fisica Nucleare"},
        ],
        [person("INFN, Laboratori Nazionali di Legnaro", "Facility for Rare Isotope Beams")],
    )

    assert names(institutes) == [
        "Facility for Rare Isotope Beams",
        "INFN, Laboratori Nazionali di Legnaro",
    ]


def test_indico_data_of_the_institute_used_by_the_authors_is_kept():
    institutes = contribution_institutes_factory(
        [{"name": "CERN", "city": "Meyrin", "country_code": "CH"}, {"name": "Other"}],
        [person("CERN")],
    )

    [cern] = institutes
    assert (cern.name, cern.city) == ("CERN", "Meyrin")


def test_institutes_sent_by_purr_are_kept_when_no_author_has_an_affiliation():
    institutes = contribution_institutes_factory(
        [{"name": "CERN"}, {"name": "A; B"}], [person(), person()]
    )

    assert names(institutes) == ["A", "B", "CERN"]
