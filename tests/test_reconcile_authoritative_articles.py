"""Source-based table reconciliation, including deliberately incorrect legacy text."""
import copy
import hashlib
import json
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path

from scripts.reconcile_authoritative_articles import (
    extract_table, parse_legacy, reconcile_items, audit, snapshot_table, main,
)


SPEC = {
    "edition": "example-2025", "pmcid": "PMC123", "pmid": "456",
    "doi": "10.1234/example", "licence": "CC-BY-4.0",
    "table_label": "Table 3", "caption_contains": "Example checklist",
    "id_from_right": 2, "text_from_right": 1,
    "item_ids": ["1a", "1b", "2"], "legacy_path": "legacy.md",
    "attribution": "Example authors (2025).",
}

XML = b"""<?xml version="1.0"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
 <front><article-meta>
  <article-id pub-id-type="doi">10.1234/example</article-id>
  <article-id pub-id-type="pmc">123</article-id>
  <article-id pub-id-type="pmid">456</article-id>
  <permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/">
  <license-p>Creative Commons Attribution 4.0 International.</license-p></license></permissions>
 </article-meta></front>
 <body><table-wrap id="Tab3"><label>Table 3.</label>
  <caption><p>Example checklist</p></caption><table><tbody>
   <tr><td colspan="3">ADMINISTRATIVE INFORMATION</td></tr>
   <tr><td rowspan="2">Title</td><td>1a</td><td>Identify the protocol.</td></tr>
   <tr><td>1b</td><td>Report any update.</td></tr>
   <tr><td>Registration</td><td>2</td><td>Provide the registration identifier.</td></tr>
  </tbody></table>
 </table-wrap></body>
</article>"""


class AuthoritativeTableTests(unittest.TestCase):
    def test_binds_source_identity_table_rows_and_subitems(self):
        data = extract_table(XML, SPEC)
        self.assertEqual([r["item_id"] for r in data["rows"]], SPEC["item_ids"])
        self.assertEqual(data["source_sha256"], hashlib.sha256(XML).hexdigest())
        self.assertEqual(data["rows"][1]["source_anchor"], "Tab3:row:3:item:1b")
        self.assertEqual(data["rows"][1]["text"], "Report any update.")
        self.assertEqual(data["rights"], "article_licence_observed_table_reuse_candidate")

    def test_rejects_wrong_source_missing_row_duplicate_and_wrong_licence(self):
        for raw in (
            XML.replace(b"10.1234/example", b"10.1234/other"),
            XML.replace(b">1b<", b">1a<"),
            XML.replace(b">1b<", b">9<"),
            XML.replace(b"/licenses/by/4.0/", b"/licenses/by-nc/4.0/"),
            XML.replace(b"Example checklist", b"Different table"),
            XML.replace(b'pub-id-type="pmc">123', b'pub-id-type="pmc">999'),
        ):
            with self.subTest(raw=raw[:90]), self.assertRaises(ValueError):
                extract_table(raw, SPEC)

    def test_requires_exact_source_pin_when_configured(self):
        spec = {**SPEC, "source_sha256": "a" * 64}
        with self.assertRaisesRegex(ValueError, "source checksum"):
            extract_table(XML, spec)

    def test_legacy_number_is_not_a_source_oracle(self):
        data = extract_table(XML, SPEC)
        legacy = parse_legacy(
            "- [ ] **1a. Heading:** Identify the protocol.\n"
            "- [ ] **1b. Wrong topic:** Provide the registration identifier.\n"
            "- [ ] **2. Incorrect:** Invent a new requirement.\n"
        )
        report = reconcile_items(data["rows"], legacy)
        self.assertEqual(report["source_item_count"], 3)
        self.assertEqual(report["exact_unique_items"], 2)
        self.assertEqual(report["items"][1]["same_number_legacy_positions"], [2])
        self.assertEqual(report["items"][1]["exact_legacy_positions"], [])
        self.assertEqual(report["items"][1]["status"], "not_exactly_reconciled")
        self.assertEqual(report["items"][2]["exact_legacy_positions"], [2])
        self.assertEqual(report["items"][2]["same_number_legacy_positions"], [3])
        self.assertEqual(report["legacy_positions_without_exact_source_match"], [3])
        self.assertEqual(report["canonical_packs_promoted"], 0)

    def test_distinguishes_unnumbered_editorial_label_and_terminal_period(self):
        source = extract_table(XML, SPEC)
        legacy = parse_legacy(
            "- [ ] **Title:** Identify the protocol\n"
            "- [ ] **1b. Update:** Report any update.\n"
            "- [ ] **Registration:** Provide the registration identifier.\n"
        )
        comparison = reconcile_items(source["rows"], legacy)
        self.assertEqual(legacy[0]["declared_item_id"], None)
        self.assertEqual(legacy[0]["text"], "Identify the protocol")
        self.assertEqual(comparison["exact_unique_items"], 2)
        self.assertEqual(comparison["items"][0]["exact_legacy_positions"], [])
        self.assertEqual(comparison["items"][0]["terminal_period_only_legacy_positions"], [1])
        self.assertEqual(comparison["terminal_period_only_unique_items"], 1)
        self.assertEqual(comparison["items"][0]["status"], "not_exactly_reconciled")

    def test_full_source_and_ordered_table_pin_are_enforced(self):
        source = extract_table(XML, SPEC)
        pinned = {**SPEC, "source_sha256": source["source_sha256"],
                  "source_bytes": source["source_bytes"],
                  "table_id": source["table_id"],
                  "table_rows_sha256": source["table_rows_sha256"]}
        self.assertEqual(extract_table(XML, pinned)["pin_status"], "matched_pinned_source")
        for key, value in (("source_bytes", 1), ("table_id", "different"),
                           ("table_rows_sha256", "f"*64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                extract_table(XML, {**pinned, key: value})

    def test_offline_snapshot_preserves_source_rows_and_rejects_mutation(self):
        source = extract_table(XML, SPEC)
        spec = {**SPEC, "source_sha256": source["source_sha256"],
                "source_bytes": source["source_bytes"], "table_id": source["table_id"],
                "table_rows_sha256": source["table_rows_sha256"]}
        snapshot = {
            "edition": SPEC["edition"], "doi": SPEC["doi"], "pmcid": SPEC["pmcid"],
            "source_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC123/fullTextXML",
            "source_sha256": source["source_sha256"],
            "licence_url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution": SPEC["attribution"],
            "rows": [{k:v for k,v in row.items() if k != "normalized_text_sha256"}
                     for row in source["rows"]],
        }
        self.assertEqual(snapshot_table(snapshot, spec)["rows"], source["rows"])
        for key, bad in (("doi", "10.1234/wrong"), ("licence_url", "https://creativecommons.org/licenses/by-nc/4.0/"),
                         ("attribution", "wrong attribution"), ("source_sha256", "f"*64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                snapshot_table({**snapshot, key:bad}, spec)
        for field, value in (("text", "A changed requirement."), ("source_anchor", "wrong"),
                             ("item_id", "9")):
            mutated = copy.deepcopy(snapshot)
            mutated["rows"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                snapshot_table(mutated, spec)

    def test_audit_preserves_unavailable_editions_and_actual_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "PMC123.xml").write_bytes(XML)
            (root / "legacy.md").write_text("- [ ] **1a. Heading:** Identify the protocol.")
            missing = {**SPEC, "edition": "absent", "pmcid": "PMC999"}
            result = audit(root, root, [SPEC, missing])
            self.assertEqual(result["summary"]["source_tables_reconciled"], 1)
            self.assertEqual(result["summary"]["source_items_extracted"], 3)
            self.assertEqual(result["summary"]["canonical_packs_promoted"], 0)
            self.assertEqual(result["editions"][1]["status"], "held")
            self.assertEqual(result["editions"][1]["error_type"], "FileNotFoundError")
            self.assertEqual(result["editions"][0]["legacy"]["exact_unique_items"], 1)


    def test_live_structure_receipt_preserves_existing_row_projection(self):
        source = extract_table(XML, SPEC)
        self.assertEqual(source["structure"]["status"], "structure_observed_not_qualified")
        self.assertEqual(source["structure"]["rows"][2]["inherited_cells"], ["Tab3:row:2:cell:1"])
        self.assertEqual(source["structure"]["rows"][2]["source_anchor"], source["rows"][1]["source_anchor"])
        self.assertIsNone(source["rows"][1]["topic"])  # Existing pinned row representation is unchanged.
        bad_layout = XML.replace(b'rowspan="2"', b'rowspan="99"')
        held = extract_table(bad_layout, SPEC)
        self.assertEqual(held["structure"]["status"], "held_unsupported_structure")
        self.assertEqual(held["rows"], source["rows"])
        self.assertEqual(held["table_rows_sha256"], source["table_rows_sha256"])

    def test_offline_audit_and_cli_are_explicit_about_absent_xml_structure(self):
        source = extract_table(XML, SPEC)
        spec = {**SPEC, "source_sha256": source["source_sha256"],
                "source_bytes": source["source_bytes"], "table_id": source["table_id"],
                "table_rows_sha256": source["table_rows_sha256"]}
        snapshot = {"edition": SPEC["edition"], "doi": SPEC["doi"], "pmcid": SPEC["pmcid"],
                    "source_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC123/fullTextXML",
                    "source_sha256": source["source_sha256"],
                    "licence_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution": SPEC["attribution"],
                    "rows": [{k: v for k, v in row.items() if k != "normalized_text_sha256"}
                             for row in source["rows"]]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            official = root / "source/official"
            official.mkdir(parents=True)
            manifest = official / "authoritative-article-editions.json"
            ledger = official / "authoritative-article-rows.json"
            manifest.write_text(json.dumps([spec]), encoding="utf-8")
            ledger.write_text(json.dumps({"schema_version": 1, "editions": [snapshot]}), encoding="utf-8")
            (root / "legacy.md").write_text("- [ ] **1a.** Identify the protocol.\n", encoding="utf-8")
            out = root / "reports/evidence.json"
            with patch("sys.argv", ["reconcile", "--root", str(root), "--output", str(out), "--require-all"]):
                self.assertEqual(main(), 0)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], 2)
            self.assertEqual(report["summary"]["structure_status_counts"], {"not_retained_in_flat_snapshot": 1})
            self.assertEqual(report["summary"]["source_items_extracted"], 3)
            self.assertEqual(report["summary"]["canonical_packs_promoted"], 0)
            for invalid_ledger in ({"schema_version": 99, "editions": [snapshot]},
                                   {"schema_version": 1, "editions": []},
                                   {"schema_version": 1, "editions": [snapshot, snapshot]}):
                ledger.write_text(json.dumps(invalid_ledger), encoding="utf-8")
                with self.assertRaises(ValueError):
                    audit(root, None, [spec])
            corrupt = copy.deepcopy(snapshot)
            corrupt["rows"][0]["text"] = "Different text."
            ledger.write_text(json.dumps({"schema_version": 1, "editions": [corrupt]}), encoding="utf-8")
            with patch("sys.argv", ["reconcile", "--root", str(root), "--output", str(out), "--require-all"]):
                self.assertEqual(main(), 1)
            self.assertEqual(json.loads(out.read_text())["editions"][0]["status"], "held")

    def test_rejects_unsupported_or_unbound_primary_xml(self):
        for raw in (b"", b"not XML", b"<not-article/>", b"<article/>",
                    b"<!ENTITY a 'x'>", XML.replace(b"<table-wrap id=\"Tab3\">", b"<table-wrap>"),
                    XML.replace(b">Identify the protocol.<", b"><"),
                    XML.replace(b'<table><tbody>', b'<permissions/><table><tbody>'),
                    XML.replace(b'pub-id-type="pmid">456', b'pub-id-type="pmid">789')):
            with self.subTest(raw=raw[:60]), self.assertRaises(ValueError):
                extract_table(raw, SPEC)

    def test_empty_legacy_is_not_an_exact_match(self):
        report = reconcile_items(extract_table(XML, SPEC)["rows"], [])
        self.assertEqual(report["exact_unique_items"], 0)
        self.assertIsNone(report["items"][0]["closest_text_candidate_only"])



    def test_shared_reader_preserves_complete_legacy_structure_without_text_leak(self):
        markdown = ("## Methods\n- [ ] **1a. Topic:** Identify the\n"
                    "    protocol.\n    - [ ] **1b.** Report any update.\n"
                    "- [ ] **S2.** Report another requirement.\n"
                    "possible ambiguous continuation.\n")
        legacy = parse_legacy(markdown)
        self.assertEqual([item["declared_item_id"] for item in legacy], ["1a", "1b", "s2"])
        self.assertEqual(legacy[0]["text"], "Identify the protocol.")
        self.assertEqual(legacy[1]["parent_position"], 1)
        self.assertEqual(legacy[2]["warnings"], ["ambiguous_unindented_continuation"])
        report = reconcile_items(extract_table(XML, SPEC)["rows"], legacy)
        self.assertEqual(report["exact_unique_items"], 2)
        self.assertEqual(report["legacy_task_anchors"][0]["line_numbers"], [2, 3])
        self.assertEqual(report["legacy_task_anchors"][1]["parent_position"], 1)
        self.assertEqual(len(report["legacy_task_anchors"][0]["normalized_text_sha256"]), 64)
        self.assertNotIn("Identify the protocol.", str(report))
        self.assertNotIn("possible ambiguous continuation", str(report))


if __name__ == "__main__":
    unittest.main()
