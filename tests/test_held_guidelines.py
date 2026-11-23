"""Distinguish the real held STARD copies from independently sourced item columns."""
from copy import deepcopy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from scripts import validate_held_guidelines as check


ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads(
    (ROOT / "tests/fixtures/held-guidelines/source-item-identities.json").read_text()
)["editions"]
STARD = json.loads(
    (ROOT / "legacy/standardflow/data/stard_checklist.json").read_text()
)


def synthetic_items(edition):
    """Exercise identifier handling, without pretending to supply source wording."""
    return [
        {"id": identifier, "description": f"Unverified test fixture {identifier}"}
        for identifier in SOURCES[edition]["item_ids"]
    ]


class HeldGuidelineTests(unittest.TestCase):
    def test_real_stard_array_fails_every_independent_source_identity(self):
        for edition, source in SOURCES.items():
            with self.subTest(edition=edition):
                result = check.compare_items(STARD["items"], source["item_ids"], STARD["items"])
                self.assertFalse(result["identifiers_match"])
                self.assertTrue(result["known_stard_copy"])
                self.assertTrue(result["errors"])

    def test_truncating_stard_to_cheers_count_cannot_hide_copied_wording(self):
        items = deepcopy(STARD["items"][:28])
        result = check.compare_items(items, SOURCES["cheers-2022"]["item_ids"], STARD["items"])
        self.assertTrue(result["identifiers_match"])
        self.assertTrue(result["known_stard_copy"])
        self.assertTrue(result["errors"])

    def test_renumbering_and_repeating_stard_to_spirit_still_fails(self):
        items = synthetic_items("spirit-2025")
        for index, item in enumerate(items):
            item["description"] = STARD["items"][index % 30]["description"]
        result = check.compare_items(items, SOURCES["spirit-2025"]["item_ids"], STARD["items"])
        self.assertTrue(result["identifiers_match"])
        self.assertTrue(result["known_stard_copy"])
        self.assertTrue(result["errors"])

    def test_equal_length_prisma_p_candidate_cannot_replace_a_subitem(self):
        items = synthetic_items("prisma-p-2015")
        items[1]["id"] = "1"
        result = check.compare_items(items, SOURCES["prisma-p-2015"]["item_ids"], STARD["items"])
        self.assertEqual(result["actual_items"], result["expected_items"])
        self.assertEqual(result["missing_identifiers"], ["1b"])
        self.assertEqual(result["unexpected_identifiers"], ["1"])
        self.assertTrue(result["errors"])

    def test_srqr_requires_its_printed_s_prefix(self):
        items = synthetic_items("srqr-2014")
        for item in items:
            item["id"] = item["id"][1:]
        result = check.compare_items(items, SOURCES["srqr-2014"]["item_ids"], STARD["items"])
        self.assertFalse(result["identifiers_match"])
        self.assertIn("S1", result["missing_identifiers"])
        self.assertIn("1", result["unexpected_identifiers"])

    def test_duplicate_with_unchanged_count_is_rejected(self):
        items = synthetic_items("cheers-2022")
        items[-1]["id"] = "1"
        result = check.compare_items(items, SOURCES["cheers-2022"]["item_ids"], STARD["items"])
        self.assertEqual(result["duplicate_identifiers"], ["1"])
        self.assertEqual(result["missing_identifiers"], ["28"])
        self.assertTrue(result["errors"])

    def test_malformed_inputs_do_not_produce_a_structural_match(self):
        for items in (None, {}, [], [None], [{"id": True}], [{"id": "1", "description": " "}]):
            with self.subTest(items=items):
                result = check.compare_items(items, ["1"], STARD["items"])
                self.assertFalse(result["identifiers_match"])
                self.assertTrue(result["errors"])

    def test_synthetic_correct_ids_establish_structure_only(self):
        result = check.compare_items(
            synthetic_items("cheers-2022"), SOURCES["cheers-2022"]["item_ids"], STARD["items"]
        )
        self.assertTrue(result["identifiers_match"])
        self.assertFalse(result["known_stard_copy"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["scope"], "printed_identifiers_and_known_stard_copy_only")

    def test_cli_rejects_held_arrays_and_preserves_both_agree_candidates(self):
        # The manual archive audit reads actual Git objects; this shallow-clone
        # unit test uses their byte-equivalent frozen items as input.
        with patch.object(check, "read_archive_json", return_value=deepcopy(STARD)):
            output = io.StringIO()
            with redirect_stdout(output):
                status = check.main()
        result = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(len(result["datasets"]), 10)
        self.assertEqual(result["datasets"][0]["label"], "AGREE")
        self.assertEqual(len(result["datasets"][0]["comparisons"]), 2)
        self.assertTrue(all(row["exact_stard_items_copy"] for row in result["datasets"]))

    def test_changed_reference_cannot_redefine_the_known_copy(self):
        changed = deepcopy(STARD)
        changed["items"][0]["description"] = "Different reference text"
        with patch.object(check, "read_archive_json", return_value=changed):
            with self.assertRaisesRegex(ValueError, "STARD reference"):
                check.audit_archive()

    def test_missing_history_is_a_distinct_nonzero_failure(self):
        failure = subprocess.CalledProcessError(128, ["git", "show"])
        with patch.object(check, "read_archive_json", side_effect=failure):
            output = io.StringIO()
            with redirect_stdout(output):
                status = check.main()
        self.assertEqual(status, 1)
        self.assertIn("Historical Git source unavailable", json.loads(output.getvalue())["error"])


if __name__ == "__main__":
    unittest.main()
