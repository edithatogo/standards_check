"""Exercise import provenance against real, isolated Git histories."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_standardflow_import import MANIFEST, check_import, git


class StandardflowImportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        git(self.root, "init", "--initial-branch=source")
        git(self.root, "config", "user.name", "Import fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        git(self.root, "config", "commit.gpgsign", "false")
        (self.root / "app.txt").write_text("preserved source\n")
        self.commit("Source fixture")
        self.source = git(self.root, "rev-parse", "HEAD")
        source_tree = git(self.root, "rev-parse", "HEAD^{tree}")
        git(self.root, "checkout", "--orphan", "archive")
        git(self.root, "rm", "-rf", ".")
        (self.root / "history.txt").write_text("Unqualified branch; history only\n")
        self.commit("Archive fixture")
        self.archive = git(self.root, "rev-parse", "HEAD")
        git(self.root, "checkout", "--orphan", "main")
        git(self.root, "rm", "-rf", ".")
        (self.root / "README.md").write_text("# Primary fixture\n")
        self.commit("Primary fixture")
        git(self.root, "merge", "--allow-unrelated-histories", "-s", "ours",
            "--no-commit", "source", "archive")
        git(self.root, "read-tree", "--prefix=legacy/standardflow/", "-u", "source")
        manifest = self.root / MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "schema_version": "dev.standardflow.legacy-import.v1",
            "source_repository": "edithatogo/standardflow",
            "source_commit": self.source,
            "source_tree": source_tree,
            "import_prefix": "legacy/standardflow",
            "source_refs": {"source": self.source, "archive": self.archive},
        }))
        self.commit("Preserve source and archive histories; import source tree")

    def commit(self, message):
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", message)

    def test_exact_import_preserves_both_histories(self):
        self.assertEqual(check_import(self.root)["preserved_revisions"], 2)

    def test_identical_snapshot_without_history_is_rejected(self):
        snapshot = git(self.root, "commit-tree", "HEAD^{tree}", "-m", "Squashed copy")
        git(self.root, "reset", "--hard", snapshot)
        with self.assertRaisesRegex(ValueError, "Source history is not preserved"):
            check_import(self.root)

    def test_missing_archive_parent_is_rejected(self):
        snapshot = git(self.root, "commit-tree", "HEAD^{tree}", "-p", self.source,
                       "-m", "Missing archived branch")
        git(self.root, "reset", "--hard", snapshot)
        with self.assertRaisesRegex(ValueError, "Source history is not preserved"):
            check_import(self.root)

    def test_changed_import_is_rejected_before_and_after_commit(self):
        path = self.root / "legacy/standardflow/app.txt"
        path.write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "tracked working-tree or index drift"):
            check_import(self.root)
        git(self.root, "add", "legacy/standardflow/app.txt")
        path.write_text("preserved source\n")
        with self.assertRaisesRegex(ValueError, "tracked working-tree or index drift"):
            check_import(self.root)
        path.write_text("changed\n")
        self.commit("Change imported bytes")
        with self.assertRaisesRegex(ValueError, "Imported tree differs"):
            check_import(self.root)


if __name__ == "__main__":
    unittest.main()
