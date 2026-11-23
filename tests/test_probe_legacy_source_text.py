"""Synthetic source/legacy comparison; never assert scientific or rights qualification."""
import tempfile
import unittest
from pathlib import Path

from scripts.probe_legacy_source_text import normalise, evaluate_text, audit, source_text


class TextProbeTests(unittest.TestCase):
    def test_unicode_exact_matching_not_equated_with_validation(self):
        self.assertEqual(normalise("ＣＨＥＥＲＳ\u00a0 2022!"), "cheers 2022")
        comparison = evaluate_text(
            "Provide a detailed description of the outcome assessment protocol.",
            ["Provide a detailed description of the outcome assessment protocol.",
             "Background", "Completely unrelated methodology statement."])
        self.assertEqual(comparison["exact_substring_matches"], 1)
        self.assertEqual(comparison["meaningful_legacy_items"], 2)
        self.assertEqual(comparison["status"], "triage_only_not_edition_verification")

    def test_bold_item_heading_does_not_obscure_exact_requirement_text(self):
        # SPIRIT 2025 legacy preview has editorial labels that can be elsewhere
        # in the original document's table; compare requirement text only.
        original = ("Roles and responsibilities 3a\n"
                    "Names, affiliations, and roles of protocol contributors.")
        markdown = "**5. Roles and responsibilities:** Names, affiliations, and roles of protocol contributors."
        result = evaluate_text(original, [markdown])
        self.assertEqual(result["meaningful_legacy_items"], 1)
        self.assertEqual(result["exact_substring_matches"], 1)
        self.assertEqual(result["status"], "triage_only_not_edition_verification")

    def test_local_original_and_absent_original_are_audited_without_text_leak(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "source/index.yml").write_text(
                "items:\n  - id: first\n    title: First\n  - id: absent\n    title: Absent\n")
            asset = root / "source/archetypes/first.txt"
            asset.parent.mkdir()
            asset.write_text("Provide a detailed description of the outcome assessment protocol.")
            view = root / "markdown/en/archetypes/first.md"
            view.parent.mkdir(parents=True)
            view.write_text("# First\n- [ ] Provide a detailed description of the outcome assessment protocol.\n")
            report = audit(root)
            self.assertEqual(report["legacy_item_count"], 2)
            self.assertEqual(report["summary"]["records_with_original_candidates"], 1)
            self.assertEqual(report["summary"]["verified_by_this_process"], 0)
            self.assertEqual(report["legacy_items"][0]["source_probes"][0]["exact_substring_matches"], 1)
            self.assertEqual(report["legacy_items"][1]["source_probes"], [])
            self.assertNotIn("Provide a detailed description", str(report))

    def test_pdf_parse_failure_is_reported_and_does_not_promote(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "source/index.yml").write_text("items:\n  - id: bad\n    title: Bad\n")
            path = root / "source/archetypes/bad.pdf"
            path.parent.mkdir()
            path.write_bytes(b"not a PDF")
            probe = audit(root)
            self.assertEqual(probe["legacy_items"][0]["source_probes"][0]["status"],
                             "extraction_failed_or_unsupported")
            self.assertEqual(probe["summary"]["verified_by_this_process"], 0)

    def test_docx_reads_existing_paragraph_and_table_sources(self):
        from docx import Document
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.docx"
            doc = Document()
            doc.add_paragraph("Synthetic protocol")
            doc.add_table(rows=1, cols=1).cell(0, 0).text = "Study characteristics"
            doc.save(path)
            text, extractor, digest = source_text(path)
            self.assertIn("Synthetic protocol", text)
            self.assertIn("Study characteristics", text)
            self.assertEqual(extractor, "python_docx_paragraphs_and_tables")
            self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
