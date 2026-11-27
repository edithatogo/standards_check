import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import equator_literal_rows as e


def git_blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw, usedforsecurity=False).hexdigest()


class LiteralRowsTests(unittest.TestCase):
    def fixture(self, rows):
        return (
            '<p class="tp-cite">10.1000/example</p>\n'
            '<p class="tp-lic">https://creativecommons.org/licenses/by/4.0/</p>\n'
            "<script>\n  const ROWS = " + json.dumps(rows) + ";\n</script>\n"
        ).encode()

    def read(self, raw):
        return e.literal_rows(raw, "10.1000/example", ["1a", "1b"])

    def test_source_structure_and_anchor_conservation(self):
        raw = self.fixture(
            ["Section", ["L", "Subheading"], ["Topic", True, [
                ["1a", "First clause."], ["1b", "If eligible, report."]
            ]]]
        )
        result = self.read(raw)
        self.assertEqual(result["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["missing_ids"], [])
        self.assertTrue(result["exact_expected_order"])
        self.assertEqual(result["rows"][1]["requirement_anchor"], "ROWS/2/2/1/1")
        self.assertEqual(result["rows"][0]["section_anchor"], "ROWS/0")
        self.assertEqual(result["rows"][0]["label_anchor"], "ROWS/1/1")
        self.assertTrue(result["rows"][0]["indented"])
        self.assertEqual(len(result["groups"]), 3)
        self.assertNotIn("If eligible", json.dumps(result))

    def test_order_duplicates_and_missing_items_stay_held(self):
        result = self.read(
            self.fixture(["S", ["T", False, [["1b", "B"], ["1b", "C"], ["9", "D"]]]])
        )
        self.assertEqual(result["missing_ids"], ["1a"])
        self.assertEqual(result["duplicate_ids"], ["1b"])
        self.assertEqual(result["extra_ids"], ["9"])
        self.assertFalse(result["exact_expected_order"])
        self.assertEqual(result["status"], "held_structural_discrepancy")

    def test_reject_executable_malformed_and_unlicensed_inputs(self):
        good = self.fixture(["S", ["T", False, [["1a", "A"], ["1b", "B"]]]])
        for raw in (
            good + good,
            good.replace(b"10.1000/example", b"10.1000/other"),
            good.replace(b"by/4.0/", b"by-nc/4.0/"),
            good.replace(b'"A"', b'fetch("https://example.invalid")'),
            good.replace(b"];", b"].map(f);"),
            self.fixture([["T", False, [["1a", "A"]]]]),
            self.fixture(["S", ["T", "true", [["1a", "A"]]]]),
            self.fixture(["S", ["T", False, [["1a", ""]]]]),
            self.fixture(["S", ["T", True, [["1a", "A"]]]]),
            b"x" * 128001,
        ):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                self.read(raw)

    def test_pin_and_cli_retain_literal_when_docx_unavailable(self):
        raw = self.fixture(["S", ["T", False, [["1a", "A"], ["1b", "B"]]]])
        spec = {"edition": "consort-2025", "doi": "10.1000/example", "table_item_ids": [["1a", "1b"]]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qmd = root / "consort.qmd"
            qmd.write_bytes(raw)
            self.assertEqual(e.pinned_bytes(qmd, git_blob(raw)), raw)
            with self.assertRaisesRegex(ValueError, "blob identity"):
                e.pinned_bytes(qmd, "0" * 40)
            prior = Path.cwd()
            try:
                os.chdir(root)
                specs = root / "source/official/priority-article-candidates.json"
                specs.parent.mkdir(parents=True)
                specs.write_text(json.dumps([spec]))
                output = root / "receipt.json"
                args = ["reader", "--source-dir", str(root), "--output", str(output)]
                with patch.object(e, "PINS", {"consort": (git_blob(raw), "0" * 40)}), patch.object(sys, "argv", args):
                    e.main()
                receipt = json.loads(output.read_text())
                result = receipt["editions"][0]
                self.assertEqual(result["status"], "held")
                self.assertEqual(result["literal"]["expected_ids_recovered"], 2)
                self.assertEqual(result["error_type"], "FileNotFoundError")
                self.assertFalse(receipt["scientific_qualification"])
            finally:
                os.chdir(prior)

    def test_docx_anchor_evidence_keeps_blocks_and_inherited_context(self):
        structure = {"blocks": [{"kind": "table", "rows": [
            {"anchor": "body/1/r1", "cells": [
                {"anchor": "body/1/r1/c1", "text_sha256": "topic-digest", "merge_origin": "body/1/r1/c1", "blocks": []},
            ]},
            {"anchor": "body/1/r2", "cells": [
                {"anchor": "body/1/r2/c1", "text_sha256": "empty", "merge_origin": "body/1/r1/c1", "blocks": []},
                {"anchor": "body/1/r2/c2", "text_sha256": "id-digest", "blocks": []},
                {"anchor": "body/1/r2/c3", "text_sha256": "req-digest", "blocks": [
                    {"anchor": "body/1/r2/c3/1", "kind": "paragraph", "text_sha256": "a", "numbering": None},
                    {"anchor": "body/1/r2/c3/2", "kind": "paragraph", "text_sha256": "b", "numbering": {"id": 1, "level": 0}},
                ]},
            ]},
        ]}]}
        rows = [{"item_id": "1", "identifier_anchor": "body/1/r2/c2", "requirement_anchor": "body/1/r2/c3"}]
        receipt = e.docx_anchor_evidence(structure, rows)
        self.assertEqual(receipt[0]["row_anchor"], "body/1/r2")
        self.assertEqual(len(receipt[0]["requirement_blocks"]), 2)
        self.assertEqual(receipt[0]["requirement_blocks"][1]["numbering"], {"id": 1, "level": 0})
        self.assertEqual(receipt[0]["other_cells"][0]["origin_text_sha256"], "topic-digest")
        self.assertEqual(receipt[0]["other_cells"][0]["merge_origin"], "body/1/r1/c1")
        self.assertEqual(e.docx_anchor_evidence(structure, [{**rows[0], "requirement_anchor": "missing"}])[0]["status"], "unbound")

    def test_actual_docx_reader_preserves_differences(self):
        from docx import Document

        raw = self.fixture(["S", ["T", False, [["1a", "A"], ["1b", "B"]]]])
        spec = {"edition": "consort-2025", "doi": "10.1000/example", "table_item_ids": [["1a", "1b"]]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "consort.qmd").write_bytes(raw)
            document = Document()
            table = document.add_table(rows=3, cols=2)
            for row, cells in zip(table.rows, [("No", "Checklist item description"), ("1a", "A"), ("1b", "C")], strict=True):
                for cell, value in zip(row.cells, cells, strict=True):
                    cell.text = value
            path = root / "consort.docx"
            document.save(path)
            result = e.observe_pair(root, "consort", spec, (git_blob(raw), git_blob(path.read_bytes())))
            self.assertEqual(result["docx"]["comparison"]["compared"], 2)
            self.assertEqual(result["docx"]["comparison"]["different_ids"], ["1b"])
            self.assertEqual(result["status"], "held_structural_discrepancy")
            self.assertFalse(result["docx"]["independent_issuer_identity_verified"])
            evidence = result["docx"]["anchor_evidence"]
            self.assertEqual([row["item_id"] for row in evidence], ["1a", "1b"])
            self.assertEqual(evidence[1]["requirement_anchor"], result["docx"]["rows"][1]["requirement_anchor"])
            self.assertEqual(evidence[1]["requirement_blocks"][0]["kind"], "paragraph")


if __name__ == "__main__":
    unittest.main()


class MarkupDiagnosticTests(unittest.TestCase):
    def test_bullet_content_is_conserved_without_discarding_numbering(self):
        from scripts.structured_source import fingerprint

        source = LiteralRowsTests().fixture(['S', ['T', False, [['1a', 'Intro:\n• A\n• B'], ['1b', 'Other']]]])
        literal = e.literal_rows(source, '10.1000/example', ['1a', '1b'])
        ref = literal['rows'][0]
        actual = {'item_id': '1a', 'status': 'observed_not_qualified', 'requirement_blocks': [
            {'anchor': f'body/1/r2/c2/{i}', 'kind': 'paragraph', 'text_sha256': fingerprint(text), 'numbering': None if i == 1 else {'id': 4, 'level': 0}}
            for i, text in enumerate(['Intro:', 'A', 'B'], 1)]}
        result = e.bullet_content_comparison(literal['rows'], [actual])
        self.assertEqual(result[0]['status'], 'content_matches_numbered_blocks')
        self.assertEqual(result[0]['literal_anchor'], ref['requirement_anchor'])
        self.assertEqual(len(result[0]['pairs']), 3)
        actual['requirement_blocks'][2]['text_sha256'] = fingerprint('C')
        self.assertEqual(e.bullet_content_comparison(literal['rows'], [actual])[0]['status'], 'held_block_mismatch')
        actual['requirement_blocks'][2]['text_sha256'] = fingerprint('B')
        actual['requirement_blocks'][2]['numbering'] = None
        self.assertEqual(e.bullet_content_comparison(literal['rows'], [actual])[0]['status'], 'held_block_mismatch')
        self.assertEqual(e.bullet_content_comparison(literal['rows'], [])[0]['status'], 'held_block_mismatch')

    def test_docx_markup_inventory_records_references_and_definitions(self):
        import io
        from zipfile import ZipFile

        ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        def xml(value):
            return f'<w:root xmlns:w="{ns}">{value}</w:root>'
        output = io.BytesIO()
        with ZipFile(output, 'w') as z:
            z.writestr('word/document.xml', xml('<w:p><w:r><w:footnoteReference w:id="2"/></w:r></w:p>'))
            z.writestr('word/footnotes.xml', xml('<w:footnote w:id="2"><w:p><w:r><w:t>Note text</w:t></w:r></w:p></w:footnote>'))
            z.writestr('word/numbering.xml', xml('<w:abstractNum w:abstractNumId="3"><w:lvl w:ilvl="0"><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/></w:lvl></w:abstractNum><w:num w:numId="4"><w:abstractNumId w:val="3"/></w:num>'))
        result = e.docx_markup_inventory(output.getvalue())
        self.assertEqual(result['body_references']['footnoteReference'], ['2'])
        self.assertEqual(result['non_body'][0]['note_ids'], ['2'])
        self.assertEqual(result['non_body'][0]['nonempty_text_nodes'], 1)
        self.assertEqual(result['numbering'][0]['levels'][0]['format'], 'bullet')
        self.assertEqual(result['numbering'][0]['num_id'], '4')
        self.assertNotIn('Note text', json.dumps(result))
