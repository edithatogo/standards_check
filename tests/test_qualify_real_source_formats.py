"""Real-source qualification assertions; no network in regression tests."""
import unittest

from scripts.qualify_real_source_formats import html_table_receipt, compare_pdf_rows
from scripts.structured_source import fingerprint, html_structure


class RealSourceQualificationTests(unittest.TestCase):
    def test_html_bound_rows_hierarchy_and_mutated_requirement(self):
        raw = b"""<table><thead><tr><th>SECTION/TOPIC</th><th>ITEM #</th>
        <th>CHECKLIST ITEM</th></tr></thead><tbody>
        <tr><td colspan="3">GROUP A</td></tr>
        <tr><td>Topic</td><td>1</td><td>Do not omit.</td></tr>
        <tr><td>Other</td><td>2</td><td>Include condition.</td></tr>
        </tbody></table>"""
        reference = [{"item_id": "1", "topic": "Topic", "text": "Do not omit."},
                     {"item_id": "2", "topic": "Other", "text": "Include condition."}]
        groups = {"GROUP A": ["1", "2"]}
        _, structure = html_structure(raw)
        result = html_table_receipt(structure, reference, groups)
        self.assertTrue(result["exact_rows_and_hierarchy"])
        self.assertEqual(result["rows"][0]["requirement_anchor"], "table/1/r3/c3")
        self.assertNotIn("Do not omit.", str(result))
        _, changed = html_structure(raw.replace(b"Do not omit.", b"Do omit."))
        self.assertFalse(html_table_receipt(changed, reference, groups)["exact_rows_and_hierarchy"])
        _, changed = html_structure(raw.replace(b"GROUP A", b"GROUP B"))
        self.assertFalse(html_table_receipt(changed, reference, groups)["exact_rows_and_hierarchy"])
        _, changed = html_structure(raw.replace(b"<td>2</td>", b"<td>1</td>"))
        self.assertFalse(html_table_receipt(changed, reference, groups)["exact_rows_and_hierarchy"])

    def test_pdf_requires_complete_text_order_and_page(self):
        rows = [{"item_id": "1", "identifier_anchor": "page/1/table/1/r2/c2",
                 "requirement_anchor": "page/1/table/1/r2/c3",
                 "requirement_sha256": fingerprint("Do not omit.")}]
        poppler = {"1": {"page": 1, "text": "Do not omit."}}
        self.assertTrue(compare_pdf_rows(rows, poppler, ["1"], {"1": 1})["exact_rows"])
        self.assertFalse(compare_pdf_rows(rows, {"1": {"page": 1, "text": "Do omit."}},
                                         ["1"], {"1": 1})["exact_rows"])
        self.assertFalse(compare_pdf_rows(rows + rows, poppler, ["1"], {"1": 1})["exact_rows"])
        self.assertFalse(compare_pdf_rows(rows, poppler, ["1"], {"1": 2})["exact_rows"])

    def test_pdf_scoring_column_cannot_substitute_requirement(self):
        rows = [{"item_id": "1", "identifier_anchor": "page/1/table/1/r2/c2",
                 "requirement_anchor": "page/1/table/1/r2/c3",
                 "requirement_sha256": fingerprint("0")}]
        self.assertFalse(compare_pdf_rows(rows, {"1": {"page": 1, "text": "Do not omit."}},
                                         ["1"], {"1": 1})["exact_rows"])

    def test_metadata_and_canonical_not_arbitrary_link_identity(self):
        from scripts.qualify_real_source_formats import DOI, html_identity
        self.assertTrue(html_identity(f'<meta name="citation_doi" content="{DOI}">'.encode()))
        self.assertTrue(html_identity(f'<link rel="canonical" href="https://link.springer.com/article/{DOI}/tables/1">'.encode()))
        self.assertFalse(html_identity(f'<a href="https://link.springer.com/article/{DOI}">Mention</a>'.encode()))
        self.assertFalse(html_identity(f'<link rel="canonical" href="https://example.com/article/{DOI}">'.encode()))

    def test_real_pinned_pdf_receipt_preserves_full_poppler_denominator(self):
        from pathlib import Path
        from scripts.qualify_real_source_formats import pdf_receipt
        from scripts.compare_ecoevo_formats import read_bounded
        raw = read_bounded(Path("source/official/prisma-2020-checklist.pdf"))
        result = pdf_receipt(raw)
        self.assertEqual(result["poppler_item_count"], 42)
        self.assertIn(result["status"], {"held", "bounded_independent_pdf_row_agreement"})
        self.assertTrue(all("text" not in row for row in result["rows"]))

    def test_missing_local_bytes_are_held(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts.qualify_real_source_formats import report
        with TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(report(root)["html"]["status"], "held_not_acquired")
            result = report(root, root / "missing.html")
            self.assertEqual(result["html"]["status"], "held")
            self.assertEqual(result["pdf"]["status"], "held")
            self.assertEqual(result["canonical_packs_promoted"], 0)

    def test_report_and_cli_with_explicit_snapshot(self):
        import json
        import sys
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from scripts.qualify_real_source_formats import main, report, DOI
        with TemporaryDirectory() as temp:
            root = Path(temp)
            official = root / "source/official"
            official.mkdir(parents=True)
            spec = {"edition": "prisma-s-2021", "doi": DOI}
            (official / "authoritative-article-editions.json").write_text(json.dumps([spec]))
            (official / "authoritative-article-rows.json").write_text(json.dumps({"editions": [spec]}))
            html = root / "table.html"
            html.write_text(f'<meta name="citation_doi" content="{DOI}"><table><tr><td>other</td></tr></table>')
            with patch("scripts.qualify_real_source_formats.snapshot_table", return_value={"rows": [], "source_sha256": "a"*64, "table_rows_sha256": "b"*64}):
                result = report(root, html)
                self.assertEqual(result["html"]["status"], "held")
                self.assertTrue(result["html"]["identity_observed"])
            output = root / "out/report.json"
            with patch.object(sys, "argv", ["qualify", "--root", str(root), "--output", str(output)]):
                main()
            self.assertEqual(json.loads(output.read_text())["canonical_packs_promoted"], 0)
