"""Source-promotion tests use the real reference text, never synthetic evidence."""
from copy import deepcopy
import hashlib
import json
import unittest

from scripts.build_prisma42_candidate import LEDGER, PINNED_PDF_SHA256, normalize
from scripts.validate_prisma_source_assurance import audit, PACK


def pack_fixture():
    """Use genuine reference content but clear the attestation for each test."""
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    pack["verification"] = {
        "status": "imported_unverified", "verified_at": None,
        "verified_by": [], "evidence": [],
    }
    return pack


def receipts(pack):
    """Receipt-format fixture only; PDF extraction is a separate acceptance job."""
    return ["source-sha256:" + PINNED_PDF_SHA256] + [
        f"item-check:{item['display_number']}:sha256:"
        + hashlib.sha256(normalize(item["verbatim_text"]).encode("utf-8")).hexdigest()
        for item in pack["requirements"]
    ]


def reconciled_fixture():
    pack = pack_fixture()
    pack["verification"] = {
        "status": "source_reconciled", "verified_at": "2026-11-19",
        "verified_by": ["Unit-test reviewer fixture"],
        "evidence": receipts(pack),
    }
    return pack


class AssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_unverified_fixture_can_report_debt_without_false_pass(self):
        result = audit(pack_fixture(), self.ledger)
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertEqual(result["errors"], [])

    def test_rejects_promotion_when_aggregate_replaces_lettered_items(self):
        pack = reconciled_fixture()
        pack["requirements"] = [
            item for item in pack["requirements"]
            if item["display_number"] not in ("10a", "10b")
        ] + [{
            "display_number": "10", "source_anchor": "prisma-2020-checklist:item:10",
            "verbatim_text": "Aggregate fixture without complete subitems",
        }]
        result = audit(pack, self.ledger)
        self.assertIn("10", result["aggregate_entries_requiring_split"])
        self.assertIn("10a", result["missing_subitems"])
        self.assertTrue(result["errors"])

    def test_complete_reference_evidence_can_be_reconciled_but_not_external(self):
        pack = reconciled_fixture()
        result = audit(pack, self.ledger)
        self.assertTrue(result["item_level_source_reconciled"])
        self.assertEqual(result["errors"], [])
        pack["verification"]["status"] = "externally_validated"
        self.assertTrue(audit(pack, self.ledger)["errors"])

    def test_receipts_preserve_the_nfkc_whitespace_normalization_contract(self):
        pack = reconciled_fixture()
        pack["requirements"][0]["verbatim_text"] = (
            "\nIdentify \t the report as a systematic review.\n"
        )
        self.assertEqual(receipts(pack), pack["verification"]["evidence"])
        self.assertTrue(audit(pack, self.ledger)["item_level_source_reconciled"])

    def test_tampered_source_text_invalidates_prior_receipts(self):
        pack = reconciled_fixture()
        self.assertTrue(audit(pack, self.ledger)["item_level_source_reconciled"])
        pack["requirements"][0]["verbatim_text"] = "Content changed without a new receipt"
        result = audit(pack, self.ledger)
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_refreshing_hashes_cannot_certify_fabricated_pack_text(self):
        pack = reconciled_fixture()
        pack["requirements"][0]["verbatim_text"] = (
            "The official checklist requires authors to omit all study limitations."
        )
        pack["verification"]["evidence"] = receipts(pack)
        result = audit(pack, self.ledger)
        self.assertFalse(result["item_text_matches_source_ledger"])
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_synthetic_text_with_self_consistent_receipts_is_not_source_evidence(self):
        pack = reconciled_fixture()
        for item in pack["requirements"]:
            item["verbatim_text"] = f"Text {item['display_number']}"
        pack["verification"]["evidence"] = receipts(pack)
        result = audit(pack, self.ledger)
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_rejects_arbitrary_source_sha_even_with_matching_source_receipt(self):
        pack = reconciled_fixture()
        pack["authority"]["source_sha256"] = "0" * 64
        pack["verification"]["evidence"][0] = "source-sha256:" + "0" * 64
        result = audit(pack, self.ledger)
        self.assertFalse(result["source_identity_matches_pin"])
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_rejects_a_different_source_url_even_with_the_real_digest(self):
        pack = reconciled_fixture()
        pack["authority"]["source_url"] = "https://example.invalid/replacement.pdf"
        result = audit(pack, self.ledger)
        self.assertFalse(result["source_identity_matches_pin"])
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_pack_anchors_must_identify_the_corresponding_item(self):
        for anchor in ("prisma-2020-checklist:item:27", "https://example.invalid", " ", None):
            with self.subTest(anchor=anchor):
                pack = reconciled_fixture()
                pack["requirements"][0]["source_anchor"] = anchor
                result = audit(pack, self.ledger)
                self.assertFalse(result["source_anchors_match_items"])
                self.assertFalse(result["item_level_source_reconciled"])
                self.assertTrue(result["errors"])

    def test_stable_requirement_ids_cannot_be_swapped_between_source_items(self):
        pack = reconciled_fixture()
        first, second = pack["requirements"][:2]
        first["id"], second["id"] = second["id"], first["id"]
        result = audit(pack, self.ledger)
        self.assertFalse(result["source_identifiers_match_items"])
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_invalid_ledger_page_binding_cannot_support_promotion(self):
        ledger = deepcopy(self.ledger)
        ledger["items"][0]["source_anchor"] = ledger["source_url"] + "#page=2"
        result = audit(reconciled_fixture(), ledger)
        self.assertFalse(result["item_level_source_reconciled"])
        self.assertTrue(result["errors"])

    def test_rejects_uncleared_licence_and_duplicate_identifiers(self):
        pack = reconciled_fixture()
        pack["rights"]["status"] = "review_required"
        pack["requirements"].append(deepcopy(pack["requirements"][0]))
        result = audit(pack, self.ledger)
        self.assertTrue(result["duplicate_identifiers"])
        self.assertFalse(result["licence_metadata_complete"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
