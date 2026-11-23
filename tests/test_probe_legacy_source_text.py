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
            self.assertEqual(extractor, "python_docx_ordered_structure")
            self.assertEqual(len(digest), 64)


    def test_nested_legacy_structure_report_is_anchored_and_does_not_leak_text(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "source/index.yml").write_text("items:\n  - id: sample\n    title: Sample\n")
            source = root / "source/archetypes/sample.txt"
            source.parent.mkdir()
            source.write_text("Report all outcomes, including adverse events.")
            view = root / "markdown/en/archetypes/sample.md"
            view.parent.mkdir(parents=True)
            view.write_text("## Results\n- [ ] **2. Outcomes:** Report all outcomes,\n"
                            "    including adverse events.\n"
                            "    - [ ] **2a.** Describe exclusions.\n"
                            "- [ ] **2a.** Report all missing data.\n", encoding="utf-8")
            report = audit(root)
            record = report["legacy_items"][0]
            structure = record["legacy_structure"]
            self.assertEqual(report["schema_version"], 3)
            self.assertEqual(report["summary"]["verified_by_this_process"], 0)
            self.assertEqual(record["legacy_item_count"], 3)
            self.assertEqual(structure["duplicate_declared_item_ids"], ["2a"])
            self.assertEqual(structure["items"][0]["line_numbers"], [2, 3])
            self.assertEqual(structure["items"][1]["parent_position"], 1)
            self.assertEqual(structure["items"][2]["section_line"], 1)
            self.assertEqual(len(structure["view_sha256"]), 64)
            self.assertEqual(record["source_probes"][0]["item_comparisons"][0]["outcome"],
                             "fidelity_phrase_present")
            self.assertNotIn("including adverse events", str(report))
            self.assertNotIn("Describe exclusions", str(report))
            self.assertNotIn("Report all missing data", str(report))

    def test_source_size_limit_is_applied_to_the_bounded_read(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "oversized.txt"
            path.write_bytes(b"abcd")
            with patch("scripts.probe_legacy_source_text.MAX_SOURCE_BYTES", 3):
                with self.assertRaisesRegex(ValueError, "source_too_large"):
                    source_text(path)




    def test_tabular_audit_preserves_anchors_and_never_promotes_archived_workbooks(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            direct = root / "source/variants"
            direct.mkdir(parents=True)
            (root / "source/index.yml").write_text("items:\n  - id: prisma-ecoevo\n    title: Synthetic\n")
            (direct / "prisma-ecoevo.csv").write_text("ID,Requirement\n1a,Report all outcomes.\n")
            archive = root / "source/archive/processed"
            archive.mkdir(parents=True)
            book = Workbook()
            book.active.append(["1a", "Report all outcomes."])
            book.save(archive / "PRISMA-EcoEvo_ExcelChecklist.xlsx")
            book.close()
            view = root / "markdown/en/variants/prisma-ecoevo.md"
            view.parent.mkdir(parents=True)
            view.write_text("- [ ] **1a.** Report all outcomes.\n")
            report = audit(root)
            self.assertEqual(report["summary"]["verified_by_this_process"], 0)
            self.assertEqual(report["summary"]["source_structure_status_counts"],
                             {"structure_observed_not_qualified": 2})
            csv, xlsx = report["legacy_items"][0]["source_probes"]
            self.assertEqual(csv["item_comparisons"][0]["exact_structural_anchors"], ["row/2/c2"])
            self.assertEqual(xlsx["item_comparisons"][0]["exact_structural_anchors"], ["sheet/1/B1"])
            self.assertEqual(xlsx["identity_basis"], "archive_filename_candidate_unverified")
            self.assertEqual(xlsx["rights"], "unassessed")
            self.assertNotIn("Report all outcomes.", str(report))


class ItemDiagnosticsTests(unittest.TestCase):
    def test_word_boundaries_and_punctuation_are_distinct_diagnostics(self):
        result = evaluate_text(
            "unreport the complete outcome assessment protocolX. Report all outcomes, including harms.",
            ["report the complete outcome assessment protocol", "Report all outcomes including harms."])
        first, second = result["item_comparisons"]
        self.assertEqual(first["lexical_occurrences"], 0)
        self.assertEqual(first["outcome"], "absent")
        self.assertEqual(result["exact_substring_matches"], 1)  # historical triage metric
        self.assertEqual(result["token_bounded_legacy_matches"], 0)
        self.assertEqual(second["lexical_occurrences"], 1)
        self.assertEqual(second["fidelity_occurrences"], 0)
        self.assertEqual(second["outcome"], "lexical_only")

    def test_short_empty_repeated_and_negated_items_are_not_silently_accepted(self):
        result = evaluate_text("Report harms. Report harms. Do not omit withdrawals.",
                               ["Report harms.", "", "omit withdrawals.", "Report all participants."])
        repeated, empty, negated, absent = result["item_comparisons"]
        self.assertEqual([row["legacy_ordinal"] for row in result["item_comparisons"]], [1, 2, 3, 4])
        self.assertTrue(repeated["short_for_legacy_metric"])
        self.assertEqual(repeated["lexical_occurrences"], 2)
        self.assertEqual(repeated["fidelity_occurrences"], 2)
        self.assertEqual(repeated["outcome"], "repeated")
        self.assertEqual(empty["outcome"], "empty_lexical")
        # Even a fidelity phrase hit within a negated sentence is NOT equivalence.
        self.assertEqual(negated["fidelity_occurrences"], 1)
        self.assertEqual(negated["outcome"], "fidelity_phrase_present")
        self.assertEqual(absent["outcome"], "absent")
        self.assertNotIn("Report harms", str(result))
        self.assertEqual(len(repeated["legacy_fidelity_sha256"]), 64)
        self.assertEqual(result["status"], "triage_only_not_edition_verification")

    def test_fidelity_preserves_case_and_punctuation_but_normalizes_whitespace(self):
        result = evaluate_text("Report\nall outcomes, including harms.",
                               ["**2. Outcomes:** Report all outcomes, including harms.",
                                "report all outcomes, including harms."])
        first, second = result["item_comparisons"]
        self.assertEqual(first["outcome"], "fidelity_phrase_present")
        self.assertEqual(first["fidelity_occurrences"], 1)
        self.assertEqual(second["lexical_occurrences"], 1)
        self.assertEqual(second["fidelity_occurrences"], 0)
        self.assertNotEqual(first["legacy_fidelity_sha256"], second["legacy_fidelity_sha256"])


if __name__ == "__main__":
    unittest.main()
