"""Real-source qualification assertions; no network in regression tests."""
import unittest

from scripts.compare_ecoevo_formats import pdf_header_role
from scripts.qualify_real_source_formats import html_table_receipt, compare_pdf_rows
from scripts.structured_source import fingerprint, html_structure


class RealSourceQualificationTests(unittest.TestCase):
    def test_pdf_header_marker_is_bounded_to_known_header(self):
        self.assertEqual(pdf_header_role("Sub(cid:2)item\nnumber"), "id")
        self.assertEqual(pdf_header_role("Sub-item"), "requirement")
        self.assertIsNone(pdf_header_role("Sub(cid:27)item number"))
        self.assertIsNone(pdf_header_role("Sub-item number plus"))
    
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
