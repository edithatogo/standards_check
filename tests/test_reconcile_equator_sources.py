"""Source-alignment guards: candidates are not validated checklist content."""
from pathlib import Path
import tempfile
import unittest

from scripts.reconcile_equator_sources import reconcile


class ReconcileEquatorSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "source").mkdir()
        self.catalogue = {
            "schema_version": 1,
            "source_repository": "https://github.com/EQUATOR-Network/equator-website",
            "source_revision": "b" * 40,
            "rights_status": "not_assessed_for_individual_guidelines",
            "published_count": 3,
            "guidelines": [
                {"id":"equator:consort","title":"CONSORT 2025 Statement: updated guideline for reporting randomised trials","acronym":"CONSORT","page_url":"https://equator-network.org/reporting-guidelines/consort/","source_path":"reporting-guidelines/consort/index.qmd","source_blob_sha":"a"*40,"metadata_status":"extracted_unverified","doi":"10.1136/bmj-2024-081123"},
                {"id":"equator:prisma","title":"The PRISMA 2020 statement: An updated guideline for reporting systematic reviews","acronym":"PRISMA 2020","page_url":"https://equator-network.org/reporting-guidelines/prisma/","source_path":"reporting-guidelines/prisma/index.qmd","source_blob_sha":"c"*40,"metadata_status":"extracted_unverified","doi":None},
                {"id":"equator:strobe-metepi","source_path":"reporting-guidelines/strobe-metepi/index.qmd","page_url":"https://equator-network.org/reporting-guidelines/strobe-metepi/","source_blob_sha":"d"*40,"metadata_status":"needs_review","metadata_issue":"Missing title"},
            ],
            "metadata_issue_count": 1,
        }

    def index(self, content):
        (self.root / "source" / "index.yml").write_text("version: 2\nitems:\n"+content,encoding="utf-8")

    def test_matches_locator_but_flags_superseded_edition_without_promotion(self):
        self.index('  - id: consort-2010\n    title: CONSORT 2010 Checklist\n    url: https://equator-network.org/reporting-guidelines/consort/\n    group: consort\n    version: "2010"\n    status: mapped\n')
        result = reconcile(self.root, self.catalogue)
        row = result["legacy_items"][0]
        self.assertEqual(row["equator_candidate"]["id"], "equator:consort")
        self.assertEqual(row["link_basis"], "equator_page_url")
        self.assertIn("possible_edition_difference", row["findings"])
        self.assertEqual(row["admission"], "unverified_candidate")
        self.assertEqual(row["rights"], "unassessed")

    def test_hashes_original_but_never_uses_it_as_ground_truth(self):
        self.index('  - id: prisma-2020\n    title: PRISMA 2020 Checklist\n    url: https://www.prisma-statement.org/\n    group: prisma\n    version: "2020"\n    status: mapped\n')
        folder = self.root / "source" / "archetypes"
        folder.mkdir()
        (folder / "prisma-2020.pdf").write_bytes(b"fake but pinned for audit")
        result = reconcile(self.root, self.catalogue)
        row = result["legacy_items"][0]
        self.assertEqual(row["equator_candidate"]["id"], "equator:prisma")
        self.assertEqual(row["source_assets"][0]["path"], "source/archetypes/prisma-2020.pdf")
        self.assertEqual(len(row["source_assets"][0]["sha256"]), 64)
        self.assertEqual(row["admission"], "unverified_candidate")
        self.assertIn("legacy_content_not_authority", row["findings"])

    def test_missing_and_ambiguous_source_stays_unresolved(self):
        self.index('  - id: ace\n    title: ACE Checklist\n    group: consort\n    variant_of: absent-parent\n    status: mapped\n')
        result = reconcile(self.root,self.catalogue)
        row = result["legacy_items"][0]
        self.assertIsNone(row["equator_candidate"])
        self.assertIn("orphan_variant_parent",row["findings"])
        self.assertIn("no_original_asset",row["findings"])
        self.assertEqual(row["admission"],"unresolved")

    def test_same_acronym_not_enough_for_abstracts_vs_acupuncture(self):
        self.index('  - id: prisma-a\n    title: PRISMA for Abstracts Checklist\n    group: prisma\n')
        self.catalogue["guidelines"].append({
            "id": "equator:prisma-acupuncture",
            "page_url": "https://equator-network.org/reporting-guidelines/prisma-acupuncture/",
            "source_path": "reporting-guidelines/prisma-acupuncture/index.qmd",
            "source_blob_sha": "e" * 40,
            "metadata_status": "extracted_unverified",
            "title": "Reporting items for systematic reviews of acupuncture: the PRISMA for acupuncture checklist",
            "acronym": "PRISMA-A",
        })
        self.catalogue["published_count"] += 1
        result = reconcile(self.root, self.catalogue)
        self.assertIsNone(result["legacy_items"][0]["equator_candidate"])

    def test_independently_scoped_count_evidence_never_promotes_legacy(self):
        import json
        self.index('  - id: spirit-2025\n    title: SPIRIT 2025 Checklist\n    version: "2025"\n')
        folder = self.root / "tests/fixtures/held-guidelines"
        folder.mkdir(parents=True)
        (folder / "source-item-identities.json").write_text(
            json.dumps({"editions": {"spirit-2025": {"item_ids": [str(i) for i in range(1, 54)]}}})
        )
        md = self.root / "markdown/en/archetypes/spirit-2025.md"
        md.parent.mkdir(parents=True)
        md.write_text("# SPIRIT\n" + "- [ ] item\n" * 32)
        result = reconcile(self.root, self.catalogue)
        self.assertEqual(result["legacy_items"][0]["independent_identifier_count"], 53)
        self.assertIn("legacy_count_differs_from_independent_identifier_fixture", result["legacy_items"][0]["findings"])
        self.assertEqual(result["summary"]["verified_legacy_checklists"], 0)

    def test_catalogue_identity_count_and_duplicate_sources_fail_closed(self):
        self.index('  - id: prisma-2020\n    title: PRISMA 2020 Checklist\n')
        broken = {**self.catalogue, "published_count": 5}
        with self.assertRaises(ValueError):reconcile(self.root,broken)
        self.index('  - id: x\n    title: X\n  - id: x\n    title: X again\n')
        with self.assertRaises(ValueError):reconcile(self.root,self.catalogue)


if __name__=="__main__":unittest.main()
