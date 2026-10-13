import asyncio
import json
from types import SimpleNamespace

from meow.services.local.event.final_proceedings.generate_contribution_doi import (
    generate_conference_doi_task,
)

EDITORS = [
    {
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario.rossi@example.org",
        "affiliation": "INFN",
    },
    {
        "first_name": "Anna",
        "last_name": "Bianchi",
        "email": "anna.bianchi@example.org",
        "affiliation": "CERN",
    },
]


def build_conference_doi(editors: list[dict]) -> dict:
    proceedings_data = SimpleNamespace(
        event=SimpleNamespace(timezone="Europe/Rome"),
        total_pages=42,
    )
    config = SimpleNamespace(generate_external_doi_url=True)
    settings = {
        "doi_context": "10.18429",
        "doi_organization": "JACoW",
        "doi_conference": "ERL2024",
        "booktitle_long": "Test Conference",
        "editorial_json": json.dumps(editors),
    }

    return asyncio.run(
        generate_conference_doi_task(proceedings_data, settings, config)
    )


def test_conference_doi_creator_name_identifiers_are_strings():
    doi = build_conference_doi(EDITORS)

    identifiers = [c["nameIdentifiers"][0]["nameIdentifier"] for c in doi["creators"]]

    # DataCite rejects anything but string or null (CAT#39)
    assert identifiers == ["0", "1"]
    assert all(isinstance(i, str) for i in identifiers)


def test_conference_doi_contributor_name_identifiers_are_strings():
    doi = build_conference_doi(EDITORS)

    identifiers = [
        c["nameIdentifiers"][0]["nameIdentifier"] for c in doi["contributors"]
    ]

    assert identifiers == ["0", "1"]
    assert all(isinstance(i, str) for i in identifiers)


def test_conference_doi_name_identifier_scheme_is_unchanged():
    doi = build_conference_doi(EDITORS)

    for person in doi["creators"] + doi["contributors"]:
        name_identifier = person["nameIdentifiers"][0]
        assert name_identifier["nameIdentifierScheme"] == "JACoW-ID"
        assert name_identifier["schemeUri"] == "https://jacow.org"


def test_conference_doi_without_editors_has_no_creators():
    doi = build_conference_doi([])

    assert doi["creators"] == []
    assert doi["contributors"] == []
