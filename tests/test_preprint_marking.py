import unittest

from meow.models.local.event.final_proceedings.contribution_model import preprint_marking


class PreprintMarkingTest(unittest.TestCase):
    def test_legacy_field_with_missing_settings(self):
        contribution = {"field_values": [{"name": "CAT_preprint_marking", "value": "I wish my paper to be marked as preprint"}]}
        self.assertTrue(preprint_marking(contribution, None, None))

    def test_default_active_value(self):
        contribution = {"field_values": [{"name": "CAT_preprint_marking", "value": "attivo"}]}
        self.assertTrue(preprint_marking(contribution, None, None))

    def test_custom_field_and_value(self):
        contribution = {"field_values": [{"name": "My marking field", "value": "enabled"}]}
        self.assertTrue(preprint_marking(contribution, "My marking field", "enabled"))

    def test_empty_settings_do_not_match_unrelated_fields(self):
        contribution = {"field_values": [{"name": "Other field", "value": "something"}]}
        self.assertFalse(preprint_marking(contribution, "", ""))

    def test_explicit_value_does_not_accept_default(self):
        contribution = {"field_values": [{"name": "CAT_preprint_marking", "value": "ATTIVO"}]}
        self.assertFalse(preprint_marking(contribution, None, "enabled"))

    def test_partial_field_name_does_not_match(self):
        contribution = {"field_values": [{"name": "other_CAT_preprint_marking", "value": "ATTIVO"}]}
        self.assertFalse(preprint_marking(contribution, None, None))


if __name__ == "__main__":
    unittest.main()