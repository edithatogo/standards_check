import unittest
from scripts.review_source_receipts import review


def receipt(*rows, articles=()):
    return {"records": list(rows), "priority_articles": list(articles),
            "summary": {"published_count": len(rows), "canonical_packs_promoted": 0}}


class ReceiptReviewTests(unittest.TestCase):
    def test_source_drift_does_not_become_repin(self):
        base = receipt({"id": "equator:a", "source_blob_sha": "old", "status": "oa_xml_candidate"})
        current = receipt({"id": "equator:a", "source_blob_sha": "new", "status": "oa_xml_candidate"})
        result = review(current, base)
        self.assertIn("source_bytes_changed", result["finding_counts"])
        self.assertEqual(result["canonical_packs_promoted"], 0)
        self.assertEqual(result["recommendations"][0]["action"],
                         "Reacquire the exact edition; compare source, rows, anchors and rights before changing pins.")

    def test_lost_record_and_provider_failure_are_not_negative_matches(self):
        base = receipt({"id": "equator:a", "status": "oa_xml_candidate"},
                       {"id": "equator:b", "status": "oa_xml_candidate"})
        current = receipt({"id": "equator:a", "status": "lookup_incomplete"})
        result = review(current, base)
        self.assertEqual(result["finding_counts"]["record_missing"], 1)
        self.assertEqual(result["finding_counts"]["provider_incomplete"], 1)
        self.assertNotIn("unresolved_identity", result["finding_counts"])

    def test_structure_and_item_drift_without_text_export(self):
        old = {"edition": "fixture", "status": "expected_numbered_rows_observed",
               "tables": [{"table_id": "T", "table_rows_sha256": "a", "items": [
                   {"item_id": "1", "source_anchor": "T:1", "normalized_text_sha256": "x"}]}]}
        new = {**old, "tables": [{"table_id": "T", "table_rows_sha256": "b", "items": [
            {"item_id": "1", "source_anchor": "T:2", "normalized_text_sha256": "x",
             "text": "DO NOT EXPORT"}], "structure": {"issues": ["unclassified_row"]}}]}
        r = review(receipt(articles=[new]), receipt(articles=[old]))
        self.assertEqual(r["finding_counts"]["table_or_item_drift"], 1)
        self.assertEqual(r["finding_counts"]["structural_hold"], 1)
        self.assertNotIn("DO NOT EXPORT", str(r))

    def test_old_authoritative_receipt_and_duplicate_guard(self):
        a = {"editions": [{"edition": "fixture", "status": "table_items_extracted_legacy_compared",
                           "source": {"source_sha256": "x", "table_rows_sha256": "y", "rows": []},
                           "legacy": {"source_item_count": 2, "exact_unique_items": 0}}]}
        self.assertEqual(review(a)["finding_counts"]["legacy_text_discrepancy"], 1)
        with self.assertRaises(ValueError):
            review(receipt({"id": "x"}, {"id": "x"}))

    def test_disappearing_table_and_nested_structure_change_are_not_silent(self):
        old = {"edition": "fixture", "status": "expected_numbered_rows_observed",
               "source_sha256": "abc", "tables": [{"table_id": "T", "table_rows_sha256": "a",
                    "structure": {"rows": [{"row": 1, "cells": [{"rowspan": 1}]}]}}]}
        changed = {**old, "tables": [{**old["tables"][0],
                     "structure": {"rows": [{"row": 1, "cells": [{"rowspan": 2}]}]}}]}
        self.assertIn("structural_drift", review(receipt(articles=[changed]), receipt(articles=[old]))["finding_counts"])
        lost = {**old, "source_sha256": None, "tables": []}
        self.assertIn("evidence_lost", review(receipt(articles=[lost]), receipt(articles=[old]))["finding_counts"])

    def test_same_receipt_no_new_drift(self):
        a = receipt({"id": "equator:a", "status": "oa_xml_candidate"})
        self.assertEqual(review(a, a)["finding_counts"], {})


if __name__ == "__main__":
    unittest.main()
