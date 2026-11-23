"""Synthetic document controls; no protected checklist text."""
import io
import unittest
from zipfile import ZipFile
from unittest.mock import patch

from docx import Document
from openpyxl import Workbook
from scripts.structured_source import extract_structure


class StructuredSourceTests(unittest.TestCase):
    def test_docx_order_spans_nested_table_and_headings(self):
        doc = Document()
        doc.add_heading("Section example", level=2)
        table = doc.add_table(rows=2, cols=3)
        table.cell(0, 0).merge(table.cell(1, 0)).text = "Inherited topic"
        table.cell(0, 1).merge(table.cell(0, 2)).text = "First requirement"
        table.cell(1, 1).text = "1a"
        cell = table.cell(1, 2)
        cell.text = "Before nested"
        nested = cell.add_table(rows=1, cols=1)
        nested.cell(0, 0).text = "Nested requirement"
        cell.add_paragraph("After nested")
        doc.add_paragraph("Closing text")
        buf = io.BytesIO()
        doc.save(buf)
        text, structure = extract_structure(buf.getvalue(), ".docx")
        self.assertEqual(text.count("Inherited topic"), 1)
        self.assertEqual(text.count("First requirement"), 1)
        self.assertLess(text.index("Section example"), text.index("First requirement"))
        self.assertLess(text.index("Before nested"), text.index("Nested requirement"))
        self.assertLess(text.index("Nested requirement"), text.index("After nested"))
        self.assertTrue(text.endswith("Closing text"))
        first, tab, last = structure["blocks"]
        self.assertEqual(first["heading_level"], 2)
        self.assertEqual(tab["rows"][0]["cells"][1]["colspan"], 2)
        self.assertEqual(tab["rows"][1]["cells"][0]["merge_origin"], "body/2/r1/c1")
        self.assertEqual(tab["rows"][1]["cells"][1]["item_id_candidate"], "1a")
        self.assertEqual(tab["rows"][1]["cells"][2]["blocks"][1]["kind"], "table")
        self.assertEqual(last["anchor"], "body/3")
        self.assertNotIn("Nested requirement", str(structure))

    def test_csv_preserves_quoted_newlines_empty_cells_and_ragged_rows(self):
        text, report = extract_structure(b'\xef\xbb\xbfID,Requirement,Notes\r\n1a,"Report\r\noutcomes",\r\n2,Other\r\n', ".csv")
        self.assertEqual(len(report["rows"]), 3)
        row = report["rows"][1]
        self.assertEqual(row["physical_lines"], [2, 3])
        self.assertEqual(row["cells"][0]["item_id_candidate"], "1a")
        self.assertTrue(row["cells"][2]["empty"])
        self.assertEqual(report["rows"][2]["physical_lines"], [4, 4])
        self.assertIn("ragged_csv_rows", report["issues"])
        self.assertIn("Report\r\noutcomes", text)
        self.assertNotIn("Report", str(report))
        with self.assertRaises(ValueError):
            extract_structure(b'1,"unfinished', ".csv")

    def test_xlsx_preserves_coordinates_merges_types_and_formula_hold(self):
        book = Workbook()
        sheet = book.active
        sheet.title = "Example worksheet"
        sheet["A1"] = "Topic"
        sheet.merge_cells("A1:B1")
        sheet["A2"] = "2b"
        sheet["B2"] = "Report example"
        sheet["C2"] = "=1+1"
        sheet["D2"] = 0
        sheet.row_dimensions[2].hidden = True
        other = book.create_sheet("Other sheet")
        other.sheet_state = "hidden"
        other["A1"] = "Hidden example"
        buf = io.BytesIO()
        book.save(buf)
        book.close()
        text, report = extract_structure(buf.getvalue(), ".xlsx")
        first, second = report["sheets"]
        self.assertEqual(first["merged_ranges"], ["A1:B1"])
        self.assertEqual(first["rows"][1]["cells"][0]["anchor"], "sheet/1/A2")
        self.assertEqual(first["rows"][1]["cells"][0]["item_id_candidate"], "2b")
        self.assertTrue(first["rows"][1]["hidden"])
        self.assertEqual(first["rows"][1]["cells"][2]["value_type"], "f")
        self.assertFalse(first["rows"][1]["cells"][3]["empty"])
        self.assertEqual(second["state"], "hidden")
        self.assertIn("formula_cells_not_evaluated", report["issues"])
        self.assertNotIn("=1+1", text)
        self.assertNotIn("Example worksheet", str(report))
        self.assertNotIn("Report example", str(report))
        with patch("scripts.structured_source.MAX_CELLS", 2), self.assertRaises(ValueError):
            extract_structure(buf.getvalue(), ".xlsx")

    def test_xlsx_merge_expansion_is_bounded_before_normal_load(self):
        book = Workbook()
        book.active.merge_cells("A1:B1")
        original = io.BytesIO()
        book.save(original)
        book.close()
        expanded = io.BytesIO()
        with ZipFile(original) as source, ZipFile(expanded, "w") as destination:
            for item in source.infolist():
                data = source.read(item)
                if item.filename == "xl/worksheets/sheet1.xml":
                    data = data.replace(b'<mergeCell ref="A1:B1"', b'<mergeCell ref="A1:XFD1048576"')
                destination.writestr(item.filename, data)
        with self.assertRaisesRegex(ValueError, "XLSX grid exceeds limit"):
            extract_structure(expanded.getvalue(), ".xlsx")

    def test_zip_and_unsupported_format_limits(self):
        buf = io.BytesIO()
        with ZipFile(buf, "w") as archive:
            archive.writestr("word/document.xml", b"x" * 100)
        with patch("scripts.structured_source.MAX_UNPACKED_BYTES", 10):
            with self.assertRaisesRegex(ValueError, "archive exceeds"):
                extract_structure(buf.getvalue(), ".docx")
        with self.assertRaises(ValueError):
            extract_structure(b"anything", ".xls")


if __name__ == "__main__":
    unittest.main()
