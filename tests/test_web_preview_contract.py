"""Guard source contracts for GitHub Pages checklist JavaScript."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WebPreviewContractTests(unittest.TestCase):
    def test_project_relative_script_and_checklist_only_controls(self):
        template = (ROOT / "templates/pandoc/html_template.html").read_text()
        builder = (ROOT / "scripts/build_pandoc.sh").read_text()
        self.assertIn("--metadata checklist_page=true", builder)
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn("--metadata checklist_page=true", makefile)
        self.assertIn('<script src="../assets/js/app.js"></script>', template)
        self.assertNotIn('src="/assets/js/app.js"', template)
        self.assertIn("$if(checklist_page)$", template)
        self.assertIn("not an independently qualified Canonical Standard Pack", template)

    def test_reuses_checklist_inputs_and_does_not_duplicate_them(self):
        script = (ROOT / "assets/js/app.js").read_text()
        self.assertIn("querySelectorAll('ul.task-list li')", script)
        self.assertIn("const checkbox = item.querySelector(", script)
        self.assertNotIn("checkbox.type = 'checkbox'", script)
        self.assertNotIn("item.prepend(checkbox)", script)


if __name__ == "__main__":
    unittest.main()
