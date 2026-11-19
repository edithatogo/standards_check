"""Regression tests for fail-closed Conductor context and inventory."""
from pathlib import Path
import tempfile
import unittest
from scripts.audit_foundation import PIN, context_errors, inventory


class AuditTests(unittest.TestCase):
    def setup_context(self, root):
        (root / "conductor").mkdir()
        (root / ".agents/skills/conductor").mkdir(parents=True)
        (root / ".agents/skills/conductor/SKILL.md").write_text("router")
        (root / ".gitmodules").write_text(
            "[submodule \"conductor\"]\n"
            "path = .agents/plugins/conductor\n"
            "url = https://github.com/gemini-cli-extensions/conductor.git\n")
        for name in ("index", "product", "tech-stack", "workflow", "roadmap", "tracks"):
            (root / "conductor" / (name + ".md")).write_text("ok")

    def test_pin_and_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.setup_context(root)
            self.assertTrue(context_errors(root, []))
            entries = [(".agents/plugins/conductor", "160000", PIN)]
            self.assertEqual(context_errors(root, entries), [])
            (root / "conductor/index.md").write_text("[bad](./missing.md)")
            self.assertTrue(any("Broken" in e for e in context_errors(root, entries)))

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
