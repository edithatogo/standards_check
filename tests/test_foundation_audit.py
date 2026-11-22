"""Regression tests for fail-closed Conductor context and inventory."""
from pathlib import Path
import tempfile
import unittest
from scripts.audit_foundation import context_errors, inventory

# The previously accepted revision reproduces drift in the original hardcoded audit.
PIN = "f06add33b598f4262a190f234828dda551db70d7"
NEXT_PIN = "b" * 40


class AuditTests(unittest.TestCase):
    def setup_context(self, root):
        (root / "conductor").mkdir()
        (root / ".agents/skills/conductor").mkdir(parents=True)
        self.write_router(root, PIN)
        (root / ".gitmodules").write_text(
            "[submodule \"conductor\"]\n"
            "path = .agents/plugins/conductor\n"
            "url = https://github.com/gemini-cli-extensions/conductor.git\n")
        for name in ("index", "product", "tech-stack", "workflow", "roadmap", "tracks"):
            (root / "conductor" / (name + ".md")).write_text("ok")

    def write_router(self, root, revision):
        (root / ".agents/skills/conductor/SKILL.md").write_text(
            "---\nname: conductor-router\nmetadata:\n"
            "  upstream: gemini-cli-extensions/conductor\n"
            f"  revision: {revision}\n---\n\nRead the project context.\n")

    def test_pin_and_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_context(root)
            self.assertTrue(context_errors(root, []))
            entries = [(".agents/plugins/conductor", "160000", PIN)]
            self.assertEqual(context_errors(root, entries), [])
            (root / "conductor/index.md").write_text("[bad](./missing.md)")
            self.assertTrue(any("Broken" in e for e in context_errors(root, entries)))

    def test_revision_update_requires_matching_gitlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_context(root)
            entries = [(".agents/plugins/conductor", "160000", PIN)]
            self.assertEqual(context_errors(root, entries), [])
            self.write_router(root, NEXT_PIN)
            self.assertIn("Conductor exact gitlink is absent or different",
                          context_errors(root, entries))
            self.assertEqual(context_errors(root, [
                (".agents/plugins/conductor", "160000", NEXT_PIN)]), [])

    def test_changed_gitlink_and_plain_file_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_context(root)
            for mode, revision in (("160000", NEXT_PIN), ("100644", PIN)):
                with self.subTest(mode=mode, revision=revision):
                    self.assertIn("Conductor exact gitlink is absent or different",
                                  context_errors(root, [
                                      (".agents/plugins/conductor", mode, revision)]))

    def test_ambiguous_or_invalid_router_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_context(root)
            router = root / ".agents/skills/conductor/SKILL.md"
            valid = router.read_text()
            invalid = (
                valid.replace(f"  revision: {PIN}\n", ""),
                valid.replace(PIN, "main"),
                valid.replace(f"  revision: {PIN}",
                              f"  revision: {PIN}\n  revision: {NEXT_PIN}"),
                valid.replace("gemini-cli-extensions/conductor", "another/repository"),
                valid.removeprefix("---\n"),
            )
            for text in invalid:
                with self.subTest(router=text):
                    router.write_text(text)
                    self.assertTrue(context_errors(root, [
                        (".agents/plugins/conductor", "160000", PIN)]))

    def test_inventory_does_not_certify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source").mkdir()
            (root / "source/item.yml").write_text("notes: TODO")
            result = inventory(root, [("source/item.yml", "100644", "abc")])
            self.assertEqual(result["placeholder_paths"], ["source/item.yml"])
            self.assertEqual(result["areas"], {"source": 1})
            self.assertFalse(result["rights_cleared"])
            self.assertFalse(result["source_reconciled"])


if __name__ == "__main__":
    unittest.main()
