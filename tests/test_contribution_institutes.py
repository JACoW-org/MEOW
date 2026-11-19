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
