"""Track #82 draft 42-item preview, with no false source promotion."""
from copy import deepcopy
import hashlib
import json
import unittest

from scripts.build_prisma42_candidate import (
    EXPECTED, LEDGER, ORIGINAL, LEGACY_PACK_SHA256, ROOT, load_legacy_pack, preview,
)


class CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = load_legacy_pack()
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_legacy_fixture_preserves_exact_pre_promotion_bytes(self):
        self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(), LEGACY_PACK_SHA256)
        self.assertEqual(len(self.old["requirements"]), 27)
        self.assertEqual(self.old["verification"]["status"], "imported_unverified")

    def test_live_42_item_pack_is_not_accepted_as_legacy_input(self):
        live = json.loads((ROOT / "packs/org.prisma/prisma/2020/pack.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "exactly 27"):
            preview(live, self.ledger)

    def test_duplicate_legacy_entry_is_not_collapsed_into_27_identifiers(self):
        old = deepcopy(self.old)
        old["requirements"].append(deepcopy(old["requirements"][0]))
        with self.assertRaisesRegex(ValueError, "exactly 27"):
            preview(old, self.ledger)

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

    def test_malformed_and_mismatched_page_fragments_fail(self):
        for fragment in ("garbage", "2", "1extra", "1#other"):
            with self.subTest(fragment=fragment):
                ledger = deepcopy(self.ledger)
                ledger["items"][0]["source_anchor"] = ledger["source_url"] + "#page=" + fragment
                with self.assertRaisesRegex(ValueError, "complete official PDF page anchor"):
                    preview(self.old, ledger)

    def test_page_and_anchor_cannot_jointly_reassign_an_official_item(self):
        ledger = deepcopy(self.ledger)
        ledger["items"][0]["page"] = 2
        ledger["items"][0]["source_anchor"] = ledger["source_url"] + "#page=2"
        with self.assertRaisesRegex(ValueError, "official PDF page 1"):
            preview(self.old, ledger)

    def test_all_anchors_cannot_be_repointed_to_another_source(self):
        ledger = deepcopy(self.ledger)
        ledger["source_url"] = "https://example.invalid/replacement.pdf"
        for entry in ledger["items"]:
            entry["source_anchor"] = f"{ledger['source_url']}#page={entry['page']}"
        with self.assertRaisesRegex(ValueError, "pinned official"):
            preview(self.old, ledger)

    def test_rejects_unsourced_source_verification_claims(self):
        ledger = deepcopy(self.ledger)
        ledger["source_bytes_verified"] = True
        with self.assertRaises(ValueError):
            preview(self.old, ledger)


if __name__ == "__main__":
    unittest.main()
