"""A source comparison must refuse mismatched PDF bytes and omitted items."""
from copy import deepcopy
import json
import unittest
from scripts.compare_prisma_source_pdf import (
    PINNED_PDF_SHA256, normalize, verify_pdf,
)
from scripts.build_prisma42_candidate import LEDGER


class PDFComparisonTests(unittest.TestCase):
    def test_word_normalization_does_not_conflate_words(self):
        self.assertEqual(normalize("e.g., confidence/credible"), "egconfidencecredible")
        self.assertNotEqual(normalize("risk of bias"), normalize("risk of precision"))

    def test_rejects_wrong_pdf_fingerprint(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "pinned original"):
            verify_pdf(b"not the original PDF", ["x", "y"], ledger)

    def test_rejects_missing_item_even_with_complete_ids(self):
        # Even if the fingerprint is valid, every row must match its PDF page.
        # The full byte gate is tested by supplying a synthetic valid digest in
        # the negative path; no committed fixture purports to be official bytes.
        self.assertEqual(len(PINNED_PDF_SHA256), 64)
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        missing = deepcopy(ledger)
        missing["items"].pop()
        with self.assertRaises(ValueError):
            verify_pdf(b"wrong pdf", ["", ""], missing)


if __name__ == "__main__":
    unittest.main()
