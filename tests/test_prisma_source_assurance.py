"""Unit tests for PRISMA rights/status promotion safety."""
from copy import deepcopy
import unittest

from scripts.validate_prisma_source_assurance import audit, EXPECTED, SUBITEMS


def pack_fixture():
    return {
        "rights": {
            "status": "cleared", "spdx": "CC-BY-4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution": "Page et al. 2021 BMJ 372:n71",
        },
        "authority": {"source_sha256": "a" * 64},
        "verification": {
            "status": "imported_unverified", "verified_at": None,
            "verified_by": [], "evidence": [],
        },
        "requirements": [
            {"display_number": number, "source_anchor": f"checklist:{number}"}
            for number in sorted(EXPECTED)
        ],
    }


class AssuranceTests(unittest.TestCase):
    def test_unverified_fixture_can_report_debt_without_false_pass(self):
        p = pack_fixture()
        result = audit(p)
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertEqual(result["errors"], [])

    def test_rejects_promotion_when_aggregate_replaces_lettered_items(self):
        p = pack_fixture()
        p["requirements"] = [
            item for item in p["requirements"] if item["display_number"] not in ("10a", "10b")
        ] + [{"display_number": "10", "source_anchor": "checklist:10"}]
        p["verification"] = {
            "status": "source_reconciled", "verified_at": "2026-11-19",
            "verified_by": ["reviewer"], "evidence": ["review:evidence"],
        }
        result = audit(p)
        self.assertIn("10", result["aggregate_entries_requiring_split"])
        self.assertIn("10a", result["missing_subitems"])
        self.assertTrue(result["errors"])

    def test_complete_evidence_can_be_reconciled_but_not_external(self):
        p = pack_fixture()
        p["verification"] = {
            "status": "source_reconciled", "verified_at": "2026-11-19",
            "verified_by": ["reviewer"], "evidence": ["source-sha256:" + "a" * 64] + [
                f"item-check:{identifier}:sha256:" + "b" * 64 for identifier in EXPECTED
            ],
        }
        result = audit(p)
        self.assertTrue(result["item_level_source_reconciled"])
        self.assertEqual(result["errors"], [])
        p["verification"]["status"] = "externally_validated"
        self.assertTrue(audit(p)["errors"])

    def test_rejects_uncleared_licence_and_duplicate_identifiers(self):
        p = pack_fixture()
        p["rights"]["status"] = "review_required"
        p["requirements"].append(deepcopy(p["requirements"][0]))
        p["verification"]["status"] = "source_reconciled"
        result = audit(p)
        self.assertTrue(result["duplicate_identifiers"])
        self.assertFalse(result["licence_metadata_complete"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
