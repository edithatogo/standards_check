"""Exercise row/pack binding without treating synthetic layout as PDF evidence."""
from copy import deepcopy
import hashlib
import json
import textwrap
import unittest
from unittest.mock import Mock, patch

from scripts.compare_prisma_source_pdf import (
    GUTTERS, PACK, PINNED_PDF_SHA256, checklist_column, extract_pdf_pages,
    normalize, verify_pdf,
)
from scripts.build_prisma42_candidate import LEDGER, ROOT


def synthetic_layout(ledger):
    """Unit-test layout only; the acceptance job extracts the actual pinned PDF."""
    pages = []
    for page in (1, 2):
        gutter = GUTTERS[page]
        lines = ["PRISMA 2020 Checklist"]
        for item in ledger["items"]:
            if item["page"] != page:
                continue
            parts = textwrap.wrap(
                item["verbatim_text"], width=75,
                break_long_words=False, break_on_hyphens=False,
            )
            lines.append(f"{item['number']:>{gutter - 4}}" + " " * 4 + parts[0])
            lines.extend(" " * gutter + part for part in parts[1:])
        pages.append("\n".join(lines))
    return pages


class PDFComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.pack = json.loads(PACK.read_text(encoding="utf-8"))
        cls.pdf = (ROOT / "source/official/prisma-2020-checklist.pdf").read_bytes()
        cls.pages = synthetic_layout(cls.ledger)

    def test_word_normalization_preserves_punctuation_and_distinct_words(self):
        self.assertEqual(normalize("e.g., confidence/credible"), "e.g.,confidence/credible")
        self.assertNotEqual(normalize("risk of bias"), normalize("risk of precision"))
        self.assertNotEqual(normalize("confidence/credible"), normalize("confidencecredible"))

    def test_wrapped_topic_labels_do_not_interrupt_checklist_text(self):
        layout = (
            "Information              6    Specify all databases. Specify the\n"
            "sources                       date when each source was last searched.\n"
        )
        self.assertEqual(
            normalize(checklist_column(layout, 1)),
            normalize("Specify all databases. Specify the date when each source was last searched.")
        )

    def test_second_page_uses_narrower_topic_gutter(self):
        layout = (
            "Study selection      16a    Describe the results of the search.\n"
            "                            The review includes a flow diagram.\n"
        )
        self.assertEqual(
            normalize(checklist_column(layout, 2)),
            normalize("Describe the results of the search. The review includes a flow diagram.")
        )

    def test_complete_numbered_rows_bind_to_current_reference_pack(self):
        result = verify_pdf(self.pdf, self.pages, self.ledger, self.pack)
        self.assertEqual(result["item_count"], 42)
        self.assertEqual(result["pdf_sha256"], PINNED_PDF_SHA256)
        self.assertTrue(result["pack_item_source_parity"])
        self.assertEqual(
            result["comparisons"][0]["comparison_method"],
            "unicode_nfkc_whitespace_ignored_numbered_row_equality",
        )

    def test_rejects_wrong_pdf_fingerprint(self):
        with self.assertRaisesRegex(ValueError, "pinned original"):
            verify_pdf(b"not the original PDF", self.pages, self.ledger, self.pack)

    def test_rejects_missing_ledger_item_after_valid_fingerprint(self):
        missing = deepcopy(self.ledger)
        missing["items"].pop()
        with self.assertRaisesRegex(ValueError, "all 42"):
            verify_pdf(self.pdf, self.pages, missing, self.pack)

    def test_rejects_missing_numbered_pdf_row(self):
        pages = list(self.pages)
        first = next(line for line in pages[0].splitlines() if line[:30].strip() == "1")
        pages[0] = pages[0].replace(first, "")
        with self.assertRaisesRegex(ValueError, "all 42 numbered"):
            verify_pdf(self.pdf, pages, self.ledger, self.pack)

    def test_rejects_duplicate_numbered_pdf_row(self):
        pages = list(self.pages)
        first = next(line for line in pages[0].splitlines() if line[:30].strip() == "1")
        pages[0] += "\n" + first
        with self.assertRaisesRegex(ValueError, "Duplicate PDF item 1"):
            verify_pdf(self.pdf, pages, self.ledger, self.pack)

    def test_rejects_numbered_pdf_rows_out_of_order(self):
        pages = list(self.pages)
        lines = pages[0].splitlines()
        first = next(i for i, line in enumerate(lines) if line[:30].strip() == "1")
        second = next(i for i, line in enumerate(lines) if line[:30].strip() == "2")
        lines[first], lines[second] = lines[second], lines[first]
        pages[0] = "\n".join(lines)
        with self.assertRaisesRegex(ValueError, "all 42 numbered"):
            verify_pdf(self.pdf, pages, self.ledger, self.pack)

    def test_another_items_text_on_the_same_page_is_not_a_match(self):
        ledger = deepcopy(self.ledger)
        ledger["items"][0]["verbatim_text"] = ledger["items"][1]["verbatim_text"]
        with self.assertRaisesRegex(ValueError, "Item 1.*complete numbered PDF row"):
            verify_pdf(self.pdf, self.pages, ledger, self.pack)

    def test_a_contiguous_fragment_is_not_a_complete_item(self):
        ledger = deepcopy(self.ledger)
        ledger["items"][0]["verbatim_text"] = "Identify"
        with self.assertRaisesRegex(ValueError, "Item 1.*complete numbered PDF row"):
            verify_pdf(self.pdf, self.pages, ledger, self.pack)

    def test_item_cannot_move_to_another_page_with_matching_text_and_anchor(self):
        ledger = deepcopy(self.ledger)
        other = next(item for item in ledger["items"] if item["number"] == "16a")
        ledger["items"][0].update(
            page=2, verbatim_text=other["verbatim_text"],
            source_anchor=ledger["source_url"] + "#page=2",
        )
        with self.assertRaisesRegex(ValueError, "official PDF page 1"):
            verify_pdf(self.pdf, self.pages, ledger, self.pack)

    def test_actual_pack_must_match_even_when_ledger_and_pdf_match(self):
        for mutation in ("text_and_fresh_hash", "source_sha_and_receipt", "anchor", "stable_ids"):
            with self.subTest(mutation=mutation):
                pack = deepcopy(self.pack)
                if mutation == "text_and_fresh_hash":
                    text = "The official checklist requires authors to omit all study limitations."
                    pack["requirements"][0]["verbatim_text"] = text
                    digest = hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()
                    pack["verification"]["evidence"] = [
                        "item-check:1:sha256:" + digest
                        if value.startswith("item-check:1:sha256:") else value
                        for value in pack["verification"]["evidence"]
                    ]
                elif mutation == "source_sha_and_receipt":
                    pack["authority"]["source_sha256"] = "0" * 64
                    pack["verification"]["evidence"][0] = "source-sha256:" + "0" * 64
                elif mutation == "anchor":
                    pack["requirements"][0]["source_anchor"] = "prisma-2020-checklist:item:27"
                else:
                    first, second = pack["requirements"][:2]
                    first["id"], second["id"] = second["id"], first["id"]
                with self.assertRaisesRegex(ValueError, "Canonical PRISMA pack"):
                    verify_pdf(self.pdf, self.pages, self.ledger, pack)

    def test_extraction_receives_exact_pinned_bytes_on_stdin(self):
        result = Mock(stdout=("\f".join(self.pages) + "\f").encode("utf-8"))
        with patch("scripts.compare_prisma_source_pdf.subprocess.run", return_value=result) as run:
            pages = extract_pdf_pages(self.pdf)
        self.assertEqual(pages, self.pages)
        self.assertEqual(run.call_args.kwargs["input"], self.pdf)
        self.assertEqual(run.call_args.args[0][-2:], ["-", "-"])

    def test_bad_pdf_bytes_never_reach_the_extractor(self):
        with patch("scripts.compare_prisma_source_pdf.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "pinned original"):
                extract_pdf_pages(b"not the original PDF")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
