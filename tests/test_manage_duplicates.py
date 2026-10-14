import unittest
from datetime import datetime
from unittest.mock import MagicMock

from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
    ContributionFieldData,
)
from meow.models.local.event.final_proceedings.event_model import (
    AffiliationData,
    PersonData,
)
from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)
from meow.services.local.event.final_proceedings.manage_duplicates import (
    extract_target_identifier,
    find_duplicate_contribution,
    manage_duplicates,
    resolve_duplicate_contributions,
)


def make_person(first_name: str, last_name: str, affiliation: str = "CERN") -> PersonData:
    return PersonData(
        id=f"{first_name}_{last_name}",
        first=first_name,
        last=last_name,
        affiliations={affiliation},
        email=f"{first_name.lower()}.{last_name.lower()}@example.org",
    )


def make_affiliation(name: str) -> AffiliationData:
    return AffiliationData(
        id=f"aff_{name}",
        name=name,
        city="Geneva",
        country_code="CH",
        postcode="1211",
        street="Route de Meyrin",
    )


def make_contribution(
    code: str,
    contrib_id: str,
    title: str = "Test Title",
    description: str = "Test Abstract",
    duplicate_of_value: str | None = None,
    duplicate_of_field_name: str = "CAT_duplicate_of",
    primary_authors: list[PersonData] | None = None,
    coauthors: list[PersonData] | None = None,
    institutes: list[AffiliationData] | None = None,
    session_id: int = 1,
    session_code: str = "SESS01",
) -> ContributionData:
    field_values = []
    if duplicate_of_value is not None:
        field_values.append(
            ContributionFieldData(name=duplicate_of_field_name, value=duplicate_of_value)
        )

    p_authors = primary_authors or []
    c_authors = coauthors or []
    insts = institutes or []

    return ContributionData(
        id=contrib_id,
        code=code,
        type="Poster",
        url=f"https://indico.jacow.org/contribution/{contrib_id}",
        title=title,
        description=description,
        session_id=session_id,
        session_code=session_code,
        start=datetime(2026, 5, 20, 10, 0),
        end=datetime(2026, 5, 20, 12, 0),
        primary_authors=list(p_authors),
        coauthors=list(c_authors),
        authors=list(p_authors) + list(c_authors),
        institutes=list(insts),
        field_values=field_values,
    )


class ManageDuplicatesTest(unittest.IsolatedAsyncioTestCase):
    def test_find_duplicate_contribution_priorities(self):
        c1 = make_contribution(code="THP123", contrib_id="101")
        c2 = make_contribution(code="101", contrib_id="202")
        contributions = [c1, c2]

        # Priority is given to programme code
        found = find_duplicate_contribution(contributions, "101")
        self.assertIs(found, c2)

        # Lookup by programme code THP123
        found = find_duplicate_contribution(contributions, "THP123")
        self.assertIs(found, c1)

        # Lookup by ID for c1
        c3 = make_contribution(code="SUP456", contrib_id="303")
        contributions = [c1, c3]
        found = find_duplicate_contribution(contributions, "101")
        self.assertIs(found, c1)

        # Empty string
        self.assertIsNone(find_duplicate_contribution(contributions, ""))

    def test_extract_target_identifier(self):
        self.assertEqual(extract_target_identifier("THP123"), "THP123")
        self.assertEqual(extract_target_identifier("  thp123  "), "thp123")
        self.assertEqual(extract_target_identifier("12952"), "12952")
        self.assertEqual(extract_target_identifier(" 12952 "), "12952")
        self.assertEqual(
            extract_target_identifier("Cloned from contribution: 12952"), "12952"
        )
        self.assertEqual(
            extract_target_identifier("Cloned from contribution: #12952"), "12952"
        )
        self.assertEqual(
            extract_target_identifier("Cloned from contribution 12952"), "12952"
        )
        self.assertEqual(
            extract_target_identifier("cloned from: 12952"), "12952"
        )
        self.assertEqual(
            extract_target_identifier("Duplicate of: THP123"), "THP123"
        )
        self.assertEqual(
            extract_target_identifier("Duplicate of THP123"), "THP123"
        )
        self.assertEqual(
            extract_target_identifier("Contribution: 12952"), "12952"
        )
        self.assertEqual(
            extract_target_identifier("Cloned from contribution: 12952 (extra notes)"),
            "12952",
        )
        self.assertEqual(extract_target_identifier(""), "")

    def test_resolve_duplicate_standard_code(self):
        author1 = make_person("Alice", "Smith", "CERN")
        author2 = make_person("Bob", "Jones", "DESY")
        aff1 = make_affiliation("CERN")
        aff2 = make_affiliation("DESY")

        original = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Original Beam Dynamics Study",
            description="Abstract detailing beam dynamics results.",
            primary_authors=[author1],
            coauthors=[author2],
            institutes=[aff1, aff2],
        )

        stale_author = make_person("Old", "Student", "OtherLab")
        stale_aff = make_affiliation("OtherLab")

        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            title="Old Working Title",
            description="Old draft abstract",
            duplicate_of_value="THP123",
            primary_authors=[stale_author],
            institutes=[stale_aff],
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        # Verify duplicate was linked to original
        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.duplicate_of.session_id, original.session_id)
        self.assertEqual(duplicate.duplicate_of.session_code, original.session_code)

        # Verify duplicate retained its own identity
        self.assertEqual(duplicate.code, "SUP456")
        self.assertEqual(duplicate.id, "202")

        # Verify metadata synchronisation (CAT issue #35)
        self.assertEqual(duplicate.title, "Original Beam Dynamics Study")
        self.assertEqual(duplicate.description, "Abstract detailing beam dynamics results.")
        self.assertEqual(duplicate.primary_authors, [author1])
        self.assertEqual(duplicate.coauthors, [author2])
        self.assertEqual(duplicate.authors, [author1, author2])
        self.assertEqual(duplicate.institutes, [aff1, aff2])

    def test_resolve_duplicate_case_insensitive_and_whitespace(self):
        original = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Synchronised Title",
            description="Synchronised Abstract",
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            duplicate_of_value="  thp123  ",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.title, "Synchronised Title")
        self.assertEqual(duplicate.description, "Synchronised Abstract")

    def test_resolve_duplicate_numeric_indico_id(self):
        original = make_contribution(
            code="THP123",
            contrib_id="12952",
            title="Synchrotron Radiation Measurements",
            description="Measurement analysis abstract.",
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            title="Unsynced Title",
            description="Unsynced Abstract",
            duplicate_of_value="12952",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNotNone(duplicate.duplicate_of)
        # Even though target was numeric ID 12952, duplicate_of.code must be canonical programme code
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.title, "Synchrotron Radiation Measurements")
        self.assertEqual(duplicate.description, "Measurement analysis abstract.")

    def test_resolve_duplicate_sentence_with_id(self):
        original = make_contribution(
            code="THP123",
            contrib_id="12952",
            title="RF Cavity Optimisation",
            description="Detailed cavity shape optimisation.",
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            duplicate_of_value="Cloned from contribution: 12952",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.title, "RF Cavity Optimisation")
        self.assertEqual(duplicate.description, "Detailed cavity shape optimisation.")

    def test_resolve_duplicate_sentence_with_hash_and_spacing(self):
        original = make_contribution(
            code="THP123",
            contrib_id="12952",
            title="Superconducting Magnet Design",
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            duplicate_of_value="Cloned from contribution: #12952",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.title, "Superconducting Magnet Design")

    def test_alias_fallback_when_settings_alias_is_generic(self):
        original = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Fallback Title",
        )
        # Indico field is named 'CAT_duplicate_of', but settings pass 'duplicate_of'
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            duplicate_of_field_name="CAT_duplicate_of",
            duplicate_of_value="THP123",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        # Call with 'duplicate_of' as alias, fallback should still find 'CAT_duplicate_of'
        resolve_duplicate_contributions(proceedings, "duplicate_of")

        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        self.assertEqual(duplicate.title, "Fallback Title")

    def test_self_reference_is_not_matched(self):
        c = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Original Title",
            duplicate_of_value="THP123",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [c]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNone(c.duplicate_of)
        self.assertEqual(c.title, "Original Title")

    def test_nonexistent_reference_leaves_duplicate_none(self):
        c = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Unchanged Title",
            duplicate_of_value="UNKNOWN999",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [c]

        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of")

        self.assertIsNone(c.duplicate_of)
        self.assertEqual(c.title, "Unchanged Title")

    async def test_manage_duplicates_async_wrapper(self):
        original = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Async Title",
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            duplicate_of_value="THP123",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        res = await manage_duplicates(proceedings, {"duplicate_of_alias": "CAT_duplicate_of"})

        self.assertIs(res, proceedings)
        self.assertEqual(duplicate.title, "Async Title")


if __name__ == "__main__":
    unittest.main()
