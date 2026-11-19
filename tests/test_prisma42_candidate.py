"""Track #82 draft 42-item preview, with no false source promotion."""
from copy import deepcopy
import json
import unittest

from scripts.build_prisma42_candidate import EXPECTED, LEDGER, ORIGINAL, preview


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(ORIGINAL.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_42_entries_and_preserved_27_legacy_identifiers(self):
        candidate = preview(self.old, self.ledger)
        self.assertEqual(
            [item["display_number"] for item in candidate["requirements"]], EXPECTED
        )
        self.assertEqual(len(candidate["requirements"]), 42)
        aliases = candidate["migration"]["legacy_to_candidate"]
        self.assertEqual(len(aliases), 27)
        self.assertEqual(aliases["PRISMA-2020:13"], [
            "PRISMA-2020:13a", "PRISMA-2020:13b", "PRISMA-2020:13c",
            "PRISMA-2020:13d", "PRISMA-2020:13e", "PRISMA-2020:13f",
        ])
        self.assertEqual(aliases["PRISMA-2020:17"], ["PRISMA-2020:17"])

    def test_no_source_promotion_and_no_fabricated_hash(self):
        candidate = preview(self.old, self.ledger)
        self.assertEqual(candidate["verification"]["status"], "imported_unverified")
        self.assertFalse(candidate["authority"]["source_bytes_verified"])
        self.assertIsNone(candidate["authority"]["source_sha256"])

    def test_missing_subitem_fails(self):
        ledger = deepcopy(self.ledger)
        ledger["items"] = [
            x for x in ledger["items"] if x["number"] != "24c"
        ]
        with self.assertRaises(ValueError):
            preview(self.old, ledger)

    def test_wrong_source_anchor_fails(self):
        ledger = deepcopy(self.ledger)
        ledger["items"][0]["source_anchor"] = "https://example.invalid"
        with self.assertRaises(ValueError):
            preview(self.old, ledger)

    def test_rejects_unsourced_source_verification_claims(self):
        ledger = deepcopy(self.ledger)
        ledger["source_bytes_verified"] = True
        with self.assertRaises(ValueError):
            preview(self.old, ledger)


if __name__ == "__main__":
    unittest.main()
