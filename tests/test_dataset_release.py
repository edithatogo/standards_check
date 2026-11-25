import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.validate_dataset_release import main, release_digest, validate


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "contracts/datasets/standardflow-metadata.v0.1.0.json"


class DatasetReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "package").mkdir()
        self.data = {
            "schema_version": "dev.standardflow.dataset-release.v1",
            "status": "ready",
            "release": {
                "id": "synthetic-metadata",
                "version": "0.1.0",
                "producer_revision": "a" * 40,
                "sources": [{
                    "uri": "https://example.org/source",
                    "revision": "b" * 40,
                    "receipt": self.write("source.json", '{"synthetic":true}\n'),
                }],
                "destination": {"repo_id": "test-owner/test-dataset", "visibility": "public"},
                "license": "cc-by-4.0",
                "attribution": ["Synthetic fixture, not actual permission or source evidence"],
                "benchmark_role": "operational",
                "package_root": "package",
                "files": [{
                    **self.write("package/data.jsonl", '{"key":"equator:synthetic","status":"held"}\n'),
                    "format": "jsonl",
                    "rows": 1,
                    "source_content_rights": "unassessed",
                    "export_permission": "approved",
                    "columns": {"key": "approved", "status": "approved"},
                }],
            },
            "reviews": {kind: None for kind in ("rights", "privacy", "secrets", "benchmark_leakage")},
            "approval": None,
        }
        self.data["release"]["files"][0]["path"] = "data.jsonl"
        self.attest()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}

    def attest(self):
        digest = release_digest(self.data["release"])
        for kind in (*self.data["reviews"], "approval"):
            record = {"kind": kind, "release_sha256": digest, "outcome": "pass",
                      "reviewer": "synthetic-fixture-only", "reviewed_at": "2026-11-25T00:00:00Z",
                      "summary": "Synthetic test evidence; not a real review or authorization"}
            ref = self.write(f"evidence/{kind}.json", json.dumps(record))
            if kind == "approval":
                self.data["approval"] = ref
            else:
                self.data["reviews"][kind] = ref

    def replace_rows(self, text):
        ref = self.write("package/data.jsonl", text)
        self.data["release"]["files"][0]["sha256"] = ref["sha256"]
        self.attest()

    def test_committed_plan_is_incomplete_and_never_publishable(self):
        plan = json.loads(PLAN.read_text())
        result = validate(plan, ROOT)
        self.assertEqual(result["status"], "planned")
        self.assertFalse(result["publishable"])
        self.assertGreater(len(result["blockers"]), 3)
        self.assertIsNone(plan["approval"])
        self.assertTrue(all(value is None for value in plan["reviews"].values()))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(PLAN)]), 0)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([str(PLAN), "--require-publishable"]), 1)

    def test_metadata_permission_is_separate_from_unassessed_source_rights(self):
        result = validate(self.data, self.root)
        self.assertTrue(result["publishable"])
        self.assertFalse(result["scientific_acceptance"])
        self.assertEqual(self.data["release"]["files"][0]["source_content_rights"], "unassessed")

    def test_file_and_every_column_need_explicit_export_permission(self):
        for field in ("file", "key", "status"):
            changed = copy.deepcopy(self.data)
            item = changed["release"]["files"][0]
            item["source_content_rights"] = "cleared"
            if field == "file":
                item["export_permission"] = None
            else:
                item["columns"][field] = None
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "export permission"):
                validate(changed, self.root)

    def test_source_text_and_reference_labels_cannot_be_smuggled_as_columns(self):
        for column in ("verbatim_text", "normalized_requirement", "reference_label", "gold_label"):
            with self.subTest(column=column):
                original = copy.deepcopy(self.data)
                self.replace_rows(json.dumps({"key": "equator:synthetic", "status": "held",
                                              column: "unreleased content"}) + "\n")
                with self.assertRaisesRegex(ValueError, "columns"):
                    validate(self.data, self.root)
                self.data["release"]["files"][0]["columns"][column] = "approved"
                self.attest()
                with self.assertRaisesRegex(ValueError, "metadata column allowlist"):
                    validate(self.data, self.root)
                self.data = original

    def test_unknown_files_are_not_silently_exported(self):
        self.write("package/source.txt", "Unapproved source text")
        with self.assertRaisesRegex(ValueError, "inventory"):
            validate(self.data, self.root)

    def test_source_prose_and_relation_labels_cannot_hide_in_metadata_values(self):
        for value, message in (("Report every outcome", "free text"), ("equivalent", "relation labels")):
            with self.subTest(value=value):
                self.replace_rows(json.dumps({"key": "equator:synthetic", "status": value}) + "\n")
                with self.assertRaisesRegex(ValueError, message):
                    validate(self.data, self.root)

    def test_mutation_after_approval_and_coordinated_rehash_require_new_review(self):
        ref = self.write("package/data.jsonl", '{"key":"equator:changed","status":"held"}\n')
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate(self.data, self.root)
        self.data["release"]["files"][0]["sha256"] = ref["sha256"]
        with self.assertRaisesRegex(ValueError, "review.*release hash"):
            validate(self.data, self.root)

    def test_missing_or_failed_privacy_secret_and_leakage_reviews_block_release(self):
        for kind in ("rights", "privacy", "secrets", "benchmark_leakage"):
            for outcome in (None, "failed"):
                changed = copy.deepcopy(self.data)
                if outcome is None:
                    changed["reviews"][kind] = None
                else:
                    ref = changed["reviews"][kind]
                    record = json.loads((self.root / ref["path"]).read_text())
                    record["outcome"] = outcome
                    changed["reviews"][kind] = self.write(ref["path"], json.dumps(record))
                with self.subTest(kind=kind, outcome=outcome), self.assertRaisesRegex(ValueError, kind):
                    validate(changed, self.root)
                self.attest()

    def test_missing_approval_and_changed_destination_block_release(self):
        changed = copy.deepcopy(self.data)
        changed["approval"] = None
        with self.assertRaisesRegex(ValueError, "approval"):
            validate(changed, self.root)
        self.data["release"]["destination"]["repo_id"] = "other-owner/other-dataset"
        with self.assertRaisesRegex(ValueError, "release hash"):
            validate(self.data, self.root)

    def test_pinned_sources_and_benchmark_role_are_required(self):
        for mutate, message in (
            (lambda d: d["release"]["sources"][0].update(revision="b" * 7), "40-character"),
            (lambda d: d["release"].update(producer_revision="main"), "40-character"),
            (lambda d: d["release"].update(benchmark_role="hidden_test"), "benchmark role"),
            (lambda d: d["release"].update(license=None), "license"),
            (lambda d: d["release"].update(attribution=[]), "attribution"),
        ):
            changed = copy.deepcopy(self.data)
            mutate(changed)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate(changed, self.root)

    def test_re_attested_source_uri_requires_https_host_without_credentials(self):
        for uri in (
            "https://", "https:///source", "http://example.org/source",
            "https://user:secret@example.org/source", "https://user@example.org/source",
            "https://@example.org/source", "https://bad host/source",
            " https://example.org/source", "https://example.org\\source",
        ):
            with self.subTest(uri=uri):
                self.data["release"]["sources"][0]["uri"] = uri
                self.attest()
                with self.assertRaisesRegex(ValueError, "HTTPS source URI"):
                    validate(self.data, self.root)

    def test_re_attested_hub_destination_requires_valid_namespace_and_name(self):
        for repo_id in (
            "../..", "./.", "owner/.", ".owner/data", "owner/data-", "owner-/data",
            "owner/data..v1", "owner/data--v1", "owner/data.git", "owner.git/data",
            "owner/data/extra", "owner/café", "owner/" + "a" * 97,
            "a" * 97 + "/data", "/data", "owner/",
        ):
            with self.subTest(repo_id=repo_id):
                self.data["release"]["destination"]["repo_id"] = repo_id
                self.attest()
                with self.assertRaisesRegex(ValueError, "Hugging Face owner/repository"):
                    validate(self.data, self.root)

    def test_re_attested_version_requires_canonical_numeric_components(self):
        for version in ("00.01.0", "01.0.0", "0.01.0", "0.1.00", "1.0", "1.0.0-rc1", "٠.1.0"):
            with self.subTest(version=version):
                self.data["release"]["version"] = version
                self.attest()
                with self.assertRaisesRegex(ValueError, "semantic version"):
                    validate(self.data, self.root)

    def test_valid_release_identifier_boundaries_remain_publishable(self):
        for version, repo_id, uri in (
            ("0.0.0", "a/b", "https://example.org"),
            ("10.20.30", "Foo_1/Bar-baz.v2", "https://example.org:443/source?v=1"),
            ("1.0.0", "a" * 96 + "/" + "b" * 96, "https://example.org/source"),
        ):
            with self.subTest(version=version, repo_id=repo_id):
                self.data["release"].update(version=version)
                self.data["release"]["destination"]["repo_id"] = repo_id
                self.data["release"]["sources"][0]["uri"] = uri
                self.attest()
                self.assertTrue(validate(self.data, self.root)["publishable"])

    def test_escape_paths_and_symlinks_are_rejected(self):
        for path in ("../outside.jsonl", "/tmp/outside.jsonl", "C:\\outside.jsonl"):
            changed = copy.deepcopy(self.data)
            changed["release"]["files"][0]["path"] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "relative path"):
                validate(changed, self.root)
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.jsonl"
            target.write_text('{"key":"equator:synthetic","status":"held"}\n')
            local = self.root / "package/data.jsonl"
            local.unlink()
            local.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                validate(self.data, self.root)

    def test_duplicate_keys_bad_counts_and_nested_payloads_fail(self):
        for text, message in (
            ('{"key":"first","key":"second","status":"held"}\n', "duplicate JSON"),
            ('{"key":"a","status":"held"}\n{"key":"a","status":"held"}\n', "row count"),
            ('{"key":"a","status":{"reference_label":"equivalent"}}\n', "value type"),
        ):
            with self.subTest(message=message):
                self.replace_rows(text)
                with self.assertRaisesRegex(ValueError, message):
                    validate(self.data, self.root)

    def test_parquet_actual_columns_are_checked(self):
        import polars as pl

        old = self.root / "package/data.jsonl"
        old.unlink()
        parquet = self.root / "package/data.parquet"
        pl.DataFrame({"key": ["equator:synthetic"], "status": ["held"]}).write_parquet(parquet)
        item = self.data["release"]["files"][0]
        item.update(path="data.parquet", format="parquet", sha256=hashlib.sha256(parquet.read_bytes()).hexdigest())
        self.attest()
        self.assertTrue(validate(self.data, self.root)["publishable"])
        pl.DataFrame({"key": ["equator:synthetic"], "status": ["held"],
                      "gold_label": ["equivalent"]}).write_parquet(parquet)
        item["sha256"] = hashlib.sha256(parquet.read_bytes()).hexdigest()
        self.attest()
        with self.assertRaisesRegex(ValueError, "columns"):
            validate(self.data, self.root)
        parquet.write_bytes(b"not parquet")
        item["sha256"] = hashlib.sha256(parquet.read_bytes()).hexdigest()
        self.attest()
        with self.assertRaisesRegex(ValueError, "Parquet unreadable"):
            validate(self.data, self.root)

    def test_unknown_contract_fields_and_unverified_status_are_rejected(self):
        for mutate in (lambda d: d.update(status="published"), lambda d: d.update(upload=True)):
            changed = copy.deepcopy(self.data)
            mutate(changed)
            with self.assertRaises(ValueError):
                validate(changed, self.root)


if __name__ == "__main__":
    unittest.main()
