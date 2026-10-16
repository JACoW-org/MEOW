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
    get_duplicate_of_code,
    is_duplicate_metadata_sync_enabled,
    manage_duplicates,
    resolve_duplicate_contributions,
    resolve_duplicate_contributions_dicts,
)
from meow.models.local.event.final_proceedings.proceedings_data_factory import (
    resolve_duplicates_of,
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

    def test_sync_disabled_by_setting(self):
        author1 = make_person("Alice", "Smith")
        original = make_contribution(
            code="THP123",
            contrib_id="101",
            title="Original Title",
            description="Original Description",
            primary_authors=[author1],
        )
        duplicate = make_contribution(
            code="SUP456",
            contrib_id="202",
            title="Duplicate Custom Title",
            description="Duplicate Custom Description",
            duplicate_of_value="THP123",
        )

        proceedings = MagicMock(spec=ProceedingsData)
        proceedings.contributions = [original, duplicate]

        # Disabled via sync_metadata=False
        resolve_duplicate_contributions(proceedings, "CAT_duplicate_of", sync_metadata=False)

        # duplicate_of link is established
        self.assertIsNotNone(duplicate.duplicate_of)
        self.assertEqual(duplicate.duplicate_of.code, "THP123")
        # But metadata is NOT overwritten
        self.assertEqual(duplicate.title, "Duplicate Custom Title")
        self.assertEqual(duplicate.description, "Duplicate Custom Description")
        self.assertEqual(duplicate.primary_authors, [])

    async def test_manage_duplicates_respects_settings(self):
        # 1. Default (enabled)
        orig = make_contribution(code="THP123", contrib_id="101", title="New Title")
        dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
        proc = MagicMock(spec=ProceedingsData)
        proc.contributions = [orig, dup]
        await manage_duplicates(proc, {"duplicate_of_alias": "CAT_duplicate_of"})
        self.assertEqual(dup.title, "New Title")

        # 2. Explicitly disabled via boolean
        orig = make_contribution(code="THP123", contrib_id="101", title="New Title")
        dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
        proc = MagicMock(spec=ProceedingsData)
        proc.contributions = [orig, dup]
        await manage_duplicates(
            proc,
            {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": False},
        )
        self.assertEqual(dup.title, "Old Title")
        self.assertIsNotNone(dup.duplicate_of)

        # 3. Explicitly disabled via string "false" / "0" / "no"
        for val in ["false", "FALSE", "0", "no", "off", "disabled"]:
            orig = make_contribution(code="THP123", contrib_id="101", title="New Title")
            dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
            proc = MagicMock(spec=ProceedingsData)
            proc.contributions = [orig, dup]
            await manage_duplicates(
                proc,
                {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": val},
            )
            self.assertEqual(dup.title, "Old Title", f"Failed for setting value {val}")
            self.assertIsNotNone(dup.duplicate_of)

        # 4. Explicitly enabled via string "true" / "1" / "yes"
        for val in ["true", "TRUE", "1", "yes", "on", "enabled"]:
            orig = make_contribution(code="THP123", contrib_id="101", title="New Title")
            dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
            proc = MagicMock(spec=ProceedingsData)
            proc.contributions = [orig, dup]
            await manage_duplicates(
                proc,
                {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": val},
            )
            self.assertEqual(dup.title, "New Title", f"Failed for setting value {val}")

        # 5. Setting alias "sync_duplicates"
        orig = make_contribution(code="THP123", contrib_id="101", title="New Title")
        dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
        proc = MagicMock(spec=ProceedingsData)
        proc.contributions = [orig, dup]
        await manage_duplicates(
            proc,
            {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicates": False},
        )
        self.assertEqual(dup.title, "Old Title")

    def test_is_duplicate_metadata_sync_enabled_helper(self):
        self.assertTrue(is_duplicate_metadata_sync_enabled({}))
        self.assertTrue(is_duplicate_metadata_sync_enabled({"sync_duplicate_metadata": True}))
        self.assertTrue(is_duplicate_metadata_sync_enabled({"sync_duplicate_metadata": "true"}))
        self.assertFalse(is_duplicate_metadata_sync_enabled({"sync_duplicate_metadata": False}))
        self.assertFalse(is_duplicate_metadata_sync_enabled({"sync_duplicate_metadata": "false"}))
        self.assertFalse(is_duplicate_metadata_sync_enabled({"duplicate_sync_metadata": "0"}))
        self.assertFalse(is_duplicate_metadata_sync_enabled({"sync_duplicates": "no"}))

    def test_resolve_duplicates_of_proceedings_factory(self):
        orig = make_contribution(code="THP123", contrib_id="101", title="Factory Title")
        dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")

        # Enabled by default
        resolve_duplicates_of([orig, dup], {"duplicate_of_alias": "CAT_duplicate_of"})
        self.assertEqual(dup.title, "Factory Title")

        # Disabled
        orig = make_contribution(code="THP123", contrib_id="101", title="Factory Title")
        dup = make_contribution(code="SUP456", contrib_id="202", title="Old Title", duplicate_of_value="THP123")
        resolve_duplicates_of(
            [orig, dup],
            {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": False},
        )
        self.assertEqual(dup.title, "Old Title")
        self.assertIsNotNone(dup.duplicate_of)

    def test_get_duplicate_of_code(self):
        # 1. Dict with field_values
        d1 = {
            "field_values": [{"name": "CAT_duplicate_of", "value": "THP123"}],
        }
        self.assertEqual(get_duplicate_of_code(d1, "CAT_duplicate_of"), "THP123")
        self.assertEqual(get_duplicate_of_code(d1, "duplicate_of"), "THP123")

        # 2. Dict with duplicate_of field directly
        d2 = {"duplicate_of": "THP123"}
        self.assertEqual(get_duplicate_of_code(d2), "THP123")

        # 3. Object
        c = make_contribution(code="SUP456", contrib_id="202", duplicate_of_value="THP123")
        self.assertEqual(get_duplicate_of_code(c, "CAT_duplicate_of"), "THP123")

    def test_resolve_duplicate_contributions_dicts_enabled(self):
        orig = {
            "id": "101",
            "code": "THP123",
            "title": "Original Dict Title",
            "description": "Original Dict Description",
            "primary_authors": [{"first_name": "Bob", "last_name": "Dylan", "affiliation": "Lab"}],
            "coauthors": [{"first_name": "Alice", "last_name": "Wonder", "affiliation": "Univ"}],
            "institutes": [{"name": "Lab"}],
            "keywords": ["optics", "fel"],
            "speakers": [{"first_name": "Bob", "last_name": "Dylan"}],
        }
        dup = {
            "id": "202",
            "code": "SUP456",
            "title": "Old Dict Title",
            "description": "Old Dict Description",
            "primary_authors": [],
            "coauthors": [],
            "institutes": [],
            "keywords": [],
            "field_values": [{"name": "CAT_duplicate_of", "value": "THP123"}],
        }

        contributions = [orig, dup]
        resolve_duplicate_contributions_dicts(contributions, {"duplicate_of_alias": "CAT_duplicate_of"})

        self.assertEqual(dup["duplicate_of"], "THP123")
        self.assertEqual(dup["title"], "Original Dict Title")
        self.assertEqual(dup["description"], "Original Dict Description")
        self.assertEqual(len(dup["primary_authors"]), 1)
        self.assertEqual(dup["primary_authors"][0]["first_name"], "Bob")
        self.assertEqual(len(dup["coauthors"]), 1)
        self.assertEqual(dup["coauthors"][0]["first_name"], "Alice")
        self.assertEqual(dup["keywords"], ["optics", "fel"])
        # Speaker fallback when duplicate has no speaker
        self.assertEqual(len(dup["speakers"]), 1)

    def test_resolve_duplicate_contributions_dicts_disabled(self):
        orig = {
            "id": "101",
            "code": "THP123",
            "title": "Original Dict Title",
            "description": "Original Dict Description",
            "primary_authors": [{"first_name": "Bob", "last_name": "Dylan"}],
        }
        dup = {
            "id": "202",
            "code": "SUP456",
            "title": "Old Dict Title",
            "description": "Old Dict Description",
            "primary_authors": [],
            "field_values": [{"name": "CAT_duplicate_of", "value": "THP123"}],
        }

        contributions = [orig, dup]
        resolve_duplicate_contributions_dicts(
            contributions,
            {"duplicate_of_alias": "CAT_duplicate_of", "sync_duplicate_metadata": False},
        )

        self.assertEqual(dup["duplicate_of"], "THP123")
        self.assertEqual(dup["title"], "Old Dict Title")
        self.assertEqual(dup["description"], "Old Dict Description")
        self.assertEqual(dup["primary_authors"], [])

    def test_resolve_duplicate_contributions_dicts_matching_strategies(self):
        orig = {
            "id": "12952",
            "code": "THP123",
            "title": "Matching Title",
            "description": "Matching Description",
            "primary_authors": [{"first_name": "Jane", "last_name": "Doe"}],
        }

        # Case 1: ID with text description
        dup1 = {
            "id": "202",
            "code": "SUP01",
            "title": "Old 1",
            "field_values": [{"name": "CAT_duplicate_of", "value": "Cloned from contribution: 12952"}],
        }
        resolve_duplicate_contributions_dicts([orig, dup1], {})
        self.assertEqual(dup1["title"], "Matching Title")

        # Case 2: numeric ID string
        dup2 = {
            "id": "203",
            "code": "SUP02",
            "title": "Old 2",
            "field_values": [{"name": "CAT_duplicate_of", "value": "12952"}],
        }
        resolve_duplicate_contributions_dicts([orig, dup2], {})
        self.assertEqual(dup2["title"], "Matching Title")

        # Case 3: lowercase code
        dup3 = {
            "id": "204",
            "code": "SUP03",
            "title": "Old 3",
            "field_values": [{"name": "CAT_duplicate_of", "value": "thp123"}],
        }
        resolve_duplicate_contributions_dicts([orig, dup3], {})
        self.assertEqual(dup3["title"], "Matching Title")


if __name__ == "__main__":
    unittest.main()
