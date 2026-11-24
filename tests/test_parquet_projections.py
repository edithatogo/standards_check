"""Conservation tests for the derived analytical snapshot (#149)."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from scripts.project_parquet import project, verify_projections, write_projections

ROOT = Path(__file__).resolve().parents[1]


def put(root, path, value):
    path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def read_rows(output, name):
    return pq.read_table(output / (name + ".parquet")).to_pylist()


def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fixture(root):
    rights = {
        "status": "cleared", "spdx": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "Synthetic author", "redistribution": "Permitted with attribution",
    }
    item = {
        "id": "S:01", "display_number": "01", "section": "Methods",
        "verbatim_text": "Café — retain 01.", "normalized_requirement": "Retain 01.",
        "guidance": None, "source_anchor": "synthetic:1",
        "rights": {"inherit_from_pack": True}, "evidence_expectations": ["span", "table"],
    }
    held = deepcopy(item)
    held.update(id="S:02", display_number=None, verbatim_text=None,
                normalized_requirement="HELD wording", guidance="HELD guidance",
                source_anchor="synthetic:2",
                rights={**rights, "status": "review_required", "spdx": None})
    pack = {
        "schema_version": "dev.standardflow.standard-pack.v1", "pack_id": "test/s/1",
        "version": "1", "kind": "reporting", "title": "Synthetic",
        "authority": {"publisher": "Synthetic", "source_url": "https://example.invalid/source",
                      "retrieved_at": "2026-01-01", "source_sha256": "a" * 64},
        "verification": {"status": "imported_unverified", "verified_at": None,
                         "verified_by": [], "evidence": []},
        "rights": rights, "relationships": [], "requirements": [item, held],
    }
    put(root, "packs/test/s/1/pack.json", pack)
    put(root, "packs/test/s/1/sources/manifest.json", {
        "schema_version": "dev.standardflow.source-manifest.v1",
        "sources": [{"id": "source-1", "role": "authoritative_source",
                     "url": "https://example.invalid/source", "retrieved_at": "2026-01-01",
                     "sha256": "a" * 64, "redistributed_in_pack": False}],
        "claim_boundary": "Synthetic only",
    })
    put(root, "source/index.yml", {"items": [{"id": "s-1", "title": "Synthetic",
                                             "version": "01", "date": "2026-01-01"}]})
    put(root, "source/equator/discovery.json", {
        "schema_version": 1, "source_repository": "https://example.invalid/repo",
        "source_revision": "b" * 40, "rights_status": "not_assessed_for_individual_guidelines",
        "published_count": 1, "guidelines": [
            {"id": "equator:s", "page_url": "https://example.invalid/s",
             "source_path": "s/index.qmd", "source_blob_sha": "c" * 40,
             "metadata_status": "not_extracted"}],
    })
    put(root, "source/official/authoritative-article-rows.json", {
        "schema_version": 1, "claim_boundary": "Not admitted", "evidence": "synthetic",
        "editions": [{"edition": "candidate-1", "doi": "10.0000/s", "pmcid": "PMC1",
                      "source_url": "https://example.invalid/candidate",
                      "source_sha256": "d" * 64, "licence_url": rights["license_url"],
                      "attribution": "Synthetic author", "rows": [
                          {"item_id": "1a", "topic": "Methods", "source_anchor": "t:1",
                           "text": "Candidate text not exported"}]}],
    })
    return pack


class ProjectionConservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.output = Path(self.tmp.name) / "export"
        self.pack = fixture(self.root)

    def test_round_trip_rights_nulls_order_and_candidate_boundary(self):
        write_projections(self.root, self.output)
        verify_projections(self.root, self.output)
        rows = read_rows(self.output, "requirements")
        self.assertEqual([r["requirement_id"] for r in rows], ["S:01", "S:02"])
        self.assertEqual([r["ordinal"] for r in rows], [0, 1])
        self.assertEqual(rows[0]["display_number"], "01")
        self.assertEqual(rows[0]["verbatim_text"], "Café — retain 01.")
        self.assertEqual(rows[0]["evidence_expectations"], ["span", "table"])
        self.assertIsNone(rows[1]["display_number"])
        self.assertIsNone(rows[1]["verbatim_text"])
        self.assertIsNone(rows[1]["normalized_requirement"])
        self.assertIsNone(rows[1]["guidance"])
        self.assertEqual(rows[1]["normalized_requirement_sha256"], fingerprint("HELD wording"))
        self.assertEqual(rows[1]["rights_status"], "review_required")
        self.assertTrue(rows[0]["rights_inherited"])
        self.assertFalse(rows[1]["rights_inherited"])
        self.assertEqual(read_rows(self.output, "packs")[0]["verification_status"],
                         "imported_unverified")
        candidate = read_rows(self.output, "candidate_rows")[0]
        self.assertFalse(candidate["canonical_admission"])
        self.assertEqual(candidate["text_sha256"], fingerprint("Candidate text not exported"))
        self.assertNotIn("text", candidate)
        self.assertEqual(read_rows(self.output, "source_index")[0]["version"], "01")
        self.assertEqual(pq.read_table(self.output / "relationships.parquet").num_rows, 0)
        self.assertEqual(read_rows(self.output, "sources")[0]["redistributed_in_pack"], False)
        self.assertFalse(read_rows(self.output, "equator_guidelines")[0]["canonical_admission"])

    def test_explicit_relationship_and_null_schema(self):
        self.pack["relationships"] = [{"predicate": "extends", "target": "test/parent/1"}]
        put(self.root, "packs/test/s/1/pack.json", self.pack)
        write_projections(self.root, self.output)
        rel = read_rows(self.output, "relationships")
        self.assertEqual([(r["pack_id"], r["predicate"], r["target"]) for r in rel],
                         [("test/s/1", "extends", "test/parent/1")])
        schema = pq.read_schema(self.output / "requirements.parquet")
        self.assertEqual(schema.field("display_number").type, pa.string())
        self.assertEqual(schema.field("ordinal").type, pa.int64())

    def test_same_count_value_mutation_is_rejected_even_with_updated_file_digest(self):
        write_projections(self.root, self.output)
        path = self.output / "requirements.parquet"
        table = pq.read_table(path)
        rows = table.to_pylist()
        rows[0]["source_anchor"] = "wrong-anchor"
        pq.write_table(pa.Table.from_pylist(rows, schema=table.schema), path)
        manifest_path = self.output / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["tables"]["requirements"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)

    def test_same_count_duplicate_and_reordering_are_rejected(self):
        write_projections(self.root, self.output)
        path = self.output / "requirements.parquet"
        table = pq.read_table(path)
        for indices in ([1, 0], [0, 0]):
            with self.subTest(indices=indices):
                pq.write_table(table.take(pa.array(indices)), path)
                with self.assertRaises(ValueError):
                    verify_projections(self.root, self.output)

    def test_missing_output_extra_output_and_manifest_drift_are_rejected(self):
        write_projections(self.root, self.output)
        extra = self.output / "unexpected.parquet"
        extra.touch()
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)
        extra.unlink()
        manifest_path = self.output / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["inputs"] = {}
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)
        (self.output / "relationships.parquet").unlink()
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)

    def test_source_byte_drift_and_duplicate_identity_rejected(self):
        write_projections(self.root, self.output)
        path = self.root / "packs/test/s/1/pack.json"
        path.write_text(path.read_text() + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)
        self.pack["requirements"].append(deepcopy(self.pack["requirements"][0]))
        put(self.root, "packs/test/s/1/pack.json", self.pack)
        with self.assertRaises(ValueError):
            project(self.root)

    def test_export_is_reproducible_and_refuses_overwrite_or_canonical_location(self):
        other = self.output.with_name("second")
        write_projections(self.root, self.output)
        write_projections(self.root, other)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()},
                         {p.name: p.read_bytes() for p in other.iterdir()})
        with self.assertRaises(ValueError):
            write_projections(self.root, self.output)
        with self.assertRaises(ValueError):
            write_projections(self.root, self.root / "packs" / "export")

    def test_discovery_count_and_schema_mutations_fail(self):
        path = self.root / "source/equator/discovery.json"
        doc = json.loads(path.read_text())
        doc["published_count"] = 2
        put(self.root, "source/equator/discovery.json", doc)
        with self.assertRaises(ValueError):
            project(self.root)
        doc["published_count"] = 1
        put(self.root, "source/equator/discovery.json", doc)
        write_projections(self.root, self.output)
        path = self.output / "requirements.parquet"
        table = pq.read_table(path)
        pq.write_table(table.drop(["guidance"]), path)
        with self.assertRaises(ValueError):
            verify_projections(self.root, self.output)


class LiveCorpusConservationTests(unittest.TestCase):
    def test_every_current_pack_and_candidate_row_is_conserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "parquet"
            write_projections(ROOT, output)
            verify_projections(ROOT, output)
            expected = []
            for path in sorted((ROOT / "packs").glob("**/pack.json")):
                pack = json.loads(path.read_text(encoding="utf-8"))
                expected.extend((pack["pack_id"], index, row["id"], row["source_anchor"])
                                for index, row in enumerate(pack["requirements"]))
            actual = read_rows(output, "requirements")
            self.assertEqual([(r["pack_id"], r["ordinal"], r["requirement_id"], r["source_anchor"])
                              for r in actual], expected)
            self.assertEqual(sum(r["requirement_count"] for r in read_rows(output, "packs")),
                             len(expected))
            source = json.loads((ROOT / "source/official/authoritative-article-rows.json").read_text())
            expected_candidates = [(edition["edition"], i, row["item_id"], row["source_anchor"],
                                    fingerprint(row["text"]))
                                   for edition in source["editions"]
                                   for i, row in enumerate(edition["rows"])]
            rows = read_rows(output, "candidate_rows")
            self.assertEqual([(r["edition"], r["ordinal"], r["item_id"], r["source_anchor"],
                               r["text_sha256"]) for r in rows], expected_candidates)
            self.assertTrue(all(not r["canonical_admission"] for r in rows))
            equator = json.loads((ROOT / "source/equator/discovery.json").read_text())
            self.assertEqual([r["guideline_id"] for r in read_rows(output, "equator_guidelines")],
                             [r["id"] for r in equator["guidelines"]])
            index = yaml.safe_load((ROOT / "source/index.yml").read_text())
            self.assertEqual([r["source_id"] for r in read_rows(output, "source_index")],
                             [r["id"] for r in index["items"]])


if __name__ == "__main__":
    unittest.main()
