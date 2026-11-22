"""Repository checks must return failure when they report invalid input."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
CHECKS = ("validate_md.sh", "validate_index.sh", "validate_sidecars.sh")


class TestRepoValidation(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        (self.root / "markdown" / "archetypes").mkdir(parents=True)
        (self.root / "source" / "archetypes").mkdir(parents=True)
        self.markdown = self.root / "markdown" / "archetypes" / "example.md"
        self.markdown.write_text("\n# Example\n", encoding="utf-8")
        self.index = self.root / "source" / "index.yml"
        self.index.write_text("items:\n  - id: example\n    title: Example\n", encoding="utf-8")
        self.sidecar = self.root / "source" / "archetypes" / "example.yml"
        self.sidecar.write_text("id: example\ntitle: Example\n", encoding="utf-8")

    def run_check(self, name):
        return subprocess.run(
            ["bash", str(SCRIPTS / name)], cwd=self.root,
            text=True, capture_output=True, check=False,
        )

    def test_valid_inputs_pass_with_optional_metadata_warnings(self):
        for name in CHECKS:
            with self.subTest(check=name):
                result = self.run_check(name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("[ERROR]", result.stderr)

    def test_markdown_filename_and_heading_errors_fail(self):
        self.markdown.unlink()
        for filename, content in (("Bad_Name.md", "# Example\n"), ("example.md", "No heading\n")):
            with self.subTest(filename=filename):
                path = self.markdown.with_name(filename)
                path.write_text(content, encoding="utf-8")
                result = self.run_check("validate_md.sh")
                path.unlink()
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("[ERROR]", result.stderr)

    def test_index_missing_required_title_fails(self):
        self.index.write_text("items:\n  - id: example\n", encoding="utf-8")
        result = self.run_check("validate_index.sh")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("missing required keys: title", result.stderr)

    def test_sidecar_required_fields_and_identity_errors_fail(self):
        for content in ("id: example\n", "title: Example\n", "id: \ntitle: Example\n",
                        "id: other\ntitle: Example\n"):
            with self.subTest(content=content):
                self.sidecar.write_text(content, encoding="utf-8")
                result = self.run_check("validate_sidecars.sh")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("[ERROR]", result.stderr)
                self.assertNotIn("Sidecar validation passed.", result.stdout)

    def test_templates_and_explicit_placeholders_remain_exempt(self):
        self.sidecar.with_name("_meta.template.yml").write_text("template\n", encoding="utf-8")
        self.sidecar.with_name("pending.yml").write_text("id: <kebab-case-id>\n", encoding="utf-8")
        result = self.run_check("validate_sidecars.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("[ERROR]", result.stderr)

    def test_only_root_index_is_excluded_from_sidecars(self):
        self.sidecar.with_name("index.yml").write_text("title: Missing ID\n", encoding="utf-8")
        result = self.run_check("validate_sidecars.sh")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("index.yml", result.stderr)

    def test_missing_corpus_directories_fail(self):
        shutil.rmtree(self.root / "markdown")
        shutil.rmtree(self.root / "source")
        for name in CHECKS:
            with self.subTest(check=name):
                result = self.run_check(name)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_aggregate_validation_propagates_each_check_failure(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in CHECKS:
            shutil.copyfile(SCRIPTS / name, scripts / name)
        # Costing metadata is a separate validator, outside these input regressions.
        (scripts / "validate_costing_reconciliation.py").write_text("", encoding="utf-8")
        (self.root / "source" / "binary.pdf").write_bytes(b"%PDF\x00TBD in binary content\n")
        valid = self.run_check("validate_repo.sh")
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn("No TBD values found.", valid.stdout)
        self.assertNotIn("[WARNING] TBD values found.", valid.stdout)
        notes = self.root / "source" / "notes.txt"
        notes.write_text("TBD: fill in source metadata\n", encoding="utf-8")
        pending = self.run_check("validate_repo.sh")
        self.assertEqual(pending.returncode, 0, pending.stderr)
        self.assertIn("[WARNING] TBD values found.", pending.stdout)
        self.assertNotIn("No TBD values found.", pending.stdout)
        notes.unlink()
        for path, invalid in (
            (self.markdown, "No heading\n"),
            (self.index, "items:\n  - id: example\n"),
            (self.sidecar, "id: other\ntitle: Example\n"),
        ):
            with self.subTest(path=path.name):
                original = path.read_text(encoding="utf-8")
                path.write_text(invalid, encoding="utf-8")
                result = self.run_check("validate_repo.sh")
                path.write_text(original, encoding="utf-8")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("Repo validation failed", result.stderr)
                self.assertNotIn("Repo validation passed.", result.stdout)

        # Simulate the source disappearing after validation but before the TBD search.
        (scripts / "validate_costing_reconciliation.py").write_text(
            "import shutil\nshutil.rmtree('source')\n", encoding="utf-8",
        )
        search_error = self.run_check("validate_repo.sh")
        self.assertNotEqual(search_error.returncode, 0, search_error.stdout)
        self.assertIn("Could not search source for TBD values", search_error.stderr)
        self.assertNotIn("Repo validation passed.", search_error.stdout)


if __name__ == "__main__":
    unittest.main()
