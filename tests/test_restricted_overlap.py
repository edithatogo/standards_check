"""The restricted corpus is simulated, never redistributed."""

import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_restricted_overlap import main, scan


class RestrictedGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = {
            "schema_version": "dev.standardflow.restricted-overlap.v1",
            "n": 3,
            "expected_references": ["r"],
            "expected_artifacts": ["o"],
            "references": [{"id": "r", "text": self.write("r.txt", "amber quills drift past ridge")}],
            "artifacts": [{
                "id": "o",
                "artifact": self.write("o.txt", "synthetic artifact"),
                "fragments": self.write("o.json", json.dumps(["amber quills", "drift past ridge"])),
                "extraction_complete": True,
            }],
        }

    def write(self, name, value):
        raw = value.encode()
        (self.root / name).write_bytes(raw)
        return {"path": name, "sha256": hashlib.sha256(raw).hexdigest()}

    def test_match_and_clear(self):
        result = scan(self.manifest, self.root)
        self.assertEqual(result["status"], "held_match")
        self.assertNotIn("quills", repr(result))
        self.manifest["artifacts"][0]["fragments"] = self.write("o.json", '["different invented material"]')
        self.assertEqual(scan(self.manifest, self.root)["status"], "clear_in_scope")

    def test_missing_or_mismatched_and_incomplete(self):
        for field, value in (("expected_artifacts", ["o", "missing"]), ("expected_references", []), ("schema_version", "invalid")):
            bad = copy.deepcopy(self.manifest)
            bad[field] = value
            with self.assertRaises(ValueError):
                scan(bad, self.root)
        bad = copy.deepcopy(self.manifest)
        bad["artifacts"][0]["extraction_complete"] = False
        with self.assertRaises(ValueError):
            scan(bad, self.root)
        (self.root / "o.txt").write_text("altered")
        with self.assertRaises(ValueError):
            scan(self.manifest, self.root)

    def test_cli_gate_exit_no_text(self):
        path = self.root / "manifest.json"
        for status, expected in (("held_match", 1), ("clear_in_scope", 0), ("held_invalid_or_missing", 1)):
            if expected == 0:
                self.manifest["artifacts"][0]["fragments"] = self.write("o.json", '["different invented material"]')
            if status == "held_invalid_or_missing":
                self.manifest["references"] = []
            path.write_text(json.dumps(self.manifest))
            output = io.StringIO()
            with patch("sys.argv", ["scan", "--manifest", str(path), "--root", str(self.root)]), contextlib.redirect_stdout(output):
                self.assertEqual(main(), expected)
            self.assertEqual(json.loads(output.getvalue())["status"], status)
            self.assertNotIn("quills", output.getvalue())
