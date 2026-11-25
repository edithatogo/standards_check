import copy
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts import validate_publication_contract as publication
from scripts.validate_publication_contract import design_digest, main, validate


ROOT = Path(__file__).resolve().parents[1]


class PublicationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.contract = json.loads((ROOT / "contracts/publication/programme.v1.json").read_text())
        self.contract["design"]["protocol"] = {
            "version": "0.1.0", **self.file("protocol.md", "Synthetic test protocol")}

    def file(self, name, content):
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def frozen(self):
        design = self.contract["design"]
        design["experiments"] = [design["experiments"][0]]
        design["inputs"] = [{"id": "fixture", "family": "synthetic", "partition": "census",
                             **self.file("input.json", "{\"synthetic\":true}")}]
        design["experiments"][0]["input_ids"] = ["fixture"]
        design["freeze_blockers"] = []
        self.contract["status"] = "frozen"
        self.contract["runs"] = []
        self.contract["freeze"] = {
            "design_sha256": design_digest(design), "commit": "a" * 40,
            "frozen_at": "2026-11-24T10:00:00+00:00",
            "decision_record": self.file("decision.md", "Synthetic fixture decision; not actual approval")}
        return self.contract

    def executed(self):
        data = self.frozen()
        data["status"] = "executed"
        data["runs"] = [{
            "id": "synthetic-run", "experiment_id": "E1", "status": "completed",
            "design_sha256": data["freeze"]["design_sha256"], "implementation_commit": "b" * 40,
            "started_at": "2026-11-24T11:00:00+00:00", "command": ["fixture-only"], "exit_code": 0,
            "artifacts": [{"role": "log", **self.file("run.log", "synthetic fixture")},
                          {"role": "results", **self.file("result.json", "{\"synthetic\":true}")}]}]
        data["claims"] = [{"id": "synthetic-claim", "status": "observed", "text": "Synthetic test only",
                           "run_ids": ["synthetic-run"], "review": self.file("review.md", "Synthetic review"),
                           "limitations": ["Not an actual experiment"]}]
        return data

    def test_committed_plan_is_valid_and_does_not_claim_execution(self):
        result = validate(json.loads((ROOT / "contracts/publication/programme.v1.json").read_text()), ROOT)
        self.assertEqual(result["status"], "planned")
        self.assertEqual(result["runs"], 0)
        self.assertEqual(result["observed_claims"], 0)
        self.assertFalse(result["scientific_acceptance"])

    def test_freeze_binds_design_and_inputs(self):
        data = self.frozen()
        self.assertEqual(validate(data, self.root)["status"], "frozen")
        data["design"]["experiments"][0]["primary_endpoint"]["definition"] = "Changed after freeze"
        with self.assertRaisesRegex(ValueError, "design hash"):
            validate(data, self.root)
        data = self.frozen()
        (self.root / "input.json").write_text("changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate(data, self.root)

    def test_blockers_missing_endpoints_and_family_leakage_rejected(self):
        data = self.frozen()
        data["design"]["freeze_blockers"] = ["unresolved sample size"]
        with self.assertRaisesRegex(ValueError, "blockers"):
            validate(data, self.root)
        data = copy.deepcopy(self.contract)
        data["design"]["experiments"][0]["primary_endpoint"]["decision_rule"] = ""
        with self.assertRaisesRegex(ValueError, "decision_rule"):
            validate(data, self.root)
        data = self.frozen()
        data["design"]["inputs"] += [
            {"id": "dev", "family": "shared", "partition": "development", **self.file("dev", "a")},
            {"id": "eval", "family": "shared", "partition": "evaluation", **self.file("eval", "b")}]
        with self.assertRaisesRegex(ValueError, "family leakage"):
            validate(data, self.root)

    def test_observed_claim_requires_completed_run_and_review(self):
        data = self.executed()
        self.assertEqual(validate(data, self.root)["observed_claims"], 1)
        for mutate in (
            lambda value: value["claims"][0].update(review=None),
            lambda value: value["runs"][0].update(status="failed", exit_code=1),
            lambda value: value["runs"][0].update(artifacts=[]),
            lambda value: value["runs"][0].update(started_at="2026-11-24T09:00:00+00:00"),
            lambda value: value["runs"][0].update(design_sha256="0" * 64),
            lambda value: value["runs"][0].update(exit_code=True),
            lambda value: value.update(status="accepted"),
        ):
            changed = copy.deepcopy(data)
            mutate(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate(changed, self.root)

    def test_planned_cannot_smuggle_runs_or_observed_claims(self):
        data = self.executed()
        data["status"] = "planned"
        with self.assertRaises(ValueError):
            validate(data, self.root)
        data = self.frozen()
        data["claims"][0].update(status="observed", run_ids=[], review=None)
        with self.assertRaisesRegex(ValueError, "claim run_ids"):
            validate(data, self.root)

    def test_family_holdout_needs_both_partitions_and_distinct_input_bytes(self):
        data = self.frozen()
        experiment = data["design"]["experiments"][0]
        experiment["kind"] = "family_holdout"
        with self.assertRaisesRegex(ValueError, "development and evaluation"):
            validate(data, self.root)
        data["design"]["inputs"] = [
            {"id": "dev", "family": "alpha", "partition": "development", **self.file("dev", "same")},
            {"id": "eval", "family": "beta", "partition": "evaluation", **self.file("eval", "same")}]
        experiment["input_ids"] = ["dev", "eval"]
        with self.assertRaisesRegex(ValueError, "identical input bytes"):
            validate(data, self.root)
        data["design"]["inputs"][1].update(self.file("eval", "different"))
        data["freeze"]["design_sha256"] = design_digest(data["design"])
        self.assertEqual(validate(data, self.root)["status"], "frozen")

    def test_failed_run_is_retained_with_held_claim(self):
        data = self.executed()
        data["runs"][0].update(status="failed", exit_code=1)
        data["runs"][0]["artifacts"] = [data["runs"][0]["artifacts"][0]]
        data["claims"][0].update(status="held", review=None)
        result = validate(data, self.root)
        self.assertEqual(result["runs"], 1)
        self.assertEqual(result["observed_claims"], 0)

    def test_symlink_outside_evidence_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "external"
            target.write_text("external")
            (self.root / "escape").symlink_to(target)
            self.contract["design"]["protocol"]["path"] = "escape"
            with self.assertRaisesRegex(ValueError, "outside root"):
                validate(self.contract, self.root)

    def test_absolute_and_traversal_paths_fail_closed(self):
        for path in ("../escape", "/etc/passwd"):
            self.contract["design"]["protocol"]["path"] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "relative path"):
                validate(self.contract, self.root)

    def test_cli_invalid_contract_returns_nonzero(self):
        path = self.root / "invalid.json"
        path.write_text("{}")
        self.assertEqual(main(["--contract", str(path), "--root", str(self.root)]), 1)

    def save_contract(self, data, name="programme.v1.json"):
        path = self.root / "contracts/publication" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def baseline(self, data):
        self.save_contract(data)
        commands = [
            ["init", "-q"], ["add", "."],
            ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "commit", "-qm", "Retain publication freeze and evidence"],
        ]
        for arguments in commands:
            subprocess.run(["git", "-C", str(self.root), *arguments], check=True,
                           capture_output=True, text=True)
        return subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()

    def test_history_rejects_rehashed_design_and_changed_freeze(self):
        original = copy.deepcopy(self.executed())
        revision = self.baseline(original)
        changed = copy.deepcopy(original)
        changed["design"]["experiments"][0]["primary_endpoint"]["decision_rule"] = "Post-hoc rule"
        changed["freeze"]["design_sha256"] = design_digest(changed["design"])
        changed["runs"][0]["design_sha256"] = changed["freeze"]["design_sha256"]
        self.assertEqual(validate(changed, self.root)["status"], "executed")
        self.save_contract(changed)
        with self.assertRaisesRegex(ValueError, "frozen design.*immutable"):
            publication.validate_contracts(self.root, revision)
        changed = copy.deepcopy(original)
        changed["freeze"]["commit"] = "c" * 40
        self.save_contract(changed)
        with self.assertRaisesRegex(ValueError, "freeze.*immutable"):
            publication.validate_contracts(self.root, revision)

    def test_history_preserves_failed_runs_claim_ids_and_observed_claims(self):
        original = copy.deepcopy(self.executed())
        failed = copy.deepcopy(original["runs"][0])
        failed.update(id="failed-run", status="failed", exit_code=1)
        failed["artifacts"] = [failed["artifacts"][0]]
        original["runs"].append(failed)
        original["claims"].append({"id": "held-claim", "status": "held", "text": "Held fixture",
                                   "run_ids": ["failed-run"], "review": None,
                                   "limitations": ["Retain unsuccessful evidence"]})
        revision = self.baseline(original)
        for mutate in (
            lambda value: value["runs"].pop(),
            lambda value: value["runs"][1].update(exit_code=2),
            lambda value: value["claims"].pop(),
            lambda value: value["claims"][0].update(text="Rewritten conclusion"),
            lambda value: value["claims"][0].update(status="held"),
        ):
            changed = copy.deepcopy(original)
            mutate(changed)
            # Keep the rest of the record structurally valid after removing a failed run.
            if len(changed["runs"]) == 1:
                changed["claims"][1]["run_ids"] = []
            self.save_contract(changed)
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, "retained|immutable"):
                publication.validate_contracts(self.root, revision)
        added = copy.deepcopy(original)
        added["runs"].append({**failed, "id": "later-failed-run"})
        self.save_contract(added)
        result = publication.validate_contracts(self.root, revision)
        self.assertEqual(result["contracts"]["contracts/publication/programme.v1.json"]["runs"], 3)

    def test_frozen_contract_can_gain_runs_and_claims_can_progress(self):
        executed = copy.deepcopy(self.executed())
        frozen = copy.deepcopy(executed)
        frozen.update(status="frozen", runs=[])
        frozen["claims"][0].update(status="planned", run_ids=[], review=None)
        revision = self.baseline(frozen)
        self.save_contract(executed)
        result = publication.validate_contracts(self.root, revision)
        self.assertTrue(result["history_checked"])
        self.assertEqual(result["contracts"]["contracts/publication/programme.v1.json"]["observed_claims"], 1)
        downgraded = copy.deepcopy(frozen)
        downgraded.update(status="planned", freeze=None)
        self.save_contract(downgraded)
        with self.assertRaisesRegex(ValueError, "freeze.*immutable"):
            publication.validate_contracts(self.root, revision)

    def test_amendment_uses_new_file_and_cannot_hide_deleted_prior_contract(self):
        original = copy.deepcopy(self.frozen())
        revision = self.baseline(original)
        amended = copy.deepcopy(original)
        amended["design"]["protocol"] = {
            "version": "0.2.0", **self.file("protocol.v0.2.0.md", "Amended synthetic protocol")}
        amended["freeze"]["design_sha256"] = design_digest(amended["design"])
        new_path = self.save_contract(amended, "programme.v2.json")
        self.assertEqual(len(publication.validate_contracts(self.root, revision)["contracts"]), 2)
        (self.root / "contracts/publication/programme.v1.json").unlink()
        with self.assertRaisesRegex(ValueError, "published contract.*retained"):
            publication.validate_contracts(self.root, revision, new_path)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "--contract", str(new_path),
                                   "--baseline-revision", revision]), 1)

    def test_default_cli_checks_every_contract_and_bad_baselines_fail(self):
        self.save_contract(self.contract)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 0)
        invalid = self.save_contract({}, "programme.v2.json")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root)]), 1)
        invalid.unlink()
        for revision in ("", "--help", "0" * 40):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                publication.validate_contracts(self.root, revision)


if __name__ == "__main__":
    unittest.main()
