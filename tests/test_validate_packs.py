"""Canonical pack validation must reject malformed or unsafe source trees."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_packs


class PackValidationTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.packs = self.root / "packs"
        self.pack = self.packs / "org.prisma/prisma/2020"
        shutil.copytree(validate_packs.PACKS / "org.prisma/prisma/2020", self.pack)

    def validate(self):
        with patch.multiple(validate_packs, ROOT=self.root, PACKS=self.packs), \
                redirect_stdout(io.StringIO()):
            validate_packs.main()

    def assert_rejected(self, diagnostic):
        errors = io.StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit) as result:
            self.validate()
        self.assertEqual(result.exception.code, 1)
        self.assertIn(diagnostic, errors.getvalue())

    def test_valid_pack_passes(self):
        self.validate()

    def test_required_title_is_not_optional(self):
        path = self.pack / "pack.json"
        pack = json.loads(path.read_text(encoding="utf-8"))
        del pack["title"]
        path.write_text(json.dumps(pack), encoding="utf-8")
        self.assert_rejected("'title' is a required property")

    def test_duplicate_requirement_identifiers_fail(self):
        path = self.pack / "pack.json"
        pack = json.loads(path.read_text(encoding="utf-8"))
        pack["requirements"].append(pack["requirements"][0])
        path.write_text(json.dumps(pack), encoding="utf-8")
        self.assert_rejected("duplicate requirement IDs")

    def test_declared_pack_identity_must_match_its_directory(self):
        self.pack.rename(self.pack.with_name("wrong-location"))
        self.assert_rejected("expected directory")

    def test_symlinked_files_cannot_escape_the_pack_tree(self):
        outside = self.root / "outside.txt"
        outside.write_text("synthetic external fixture", encoding="utf-8")
        try:
            (self.pack / "external.txt").symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Platform cannot create the symlink fixture: {error}")
        self.assert_rejected("symbolic links are prohibited")


if __name__ == "__main__":
    unittest.main()
