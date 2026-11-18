"""Exercise HTML generation while isolating the yq and Pandoc process boundaries."""

import html
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_html_index.sh"

YQ_STUB = r'''
import json
import re
import sys

query, filename = sys.argv[-2:]
with open(filename, encoding="utf-8") as source:
    items = json.load(source)["items"]
if query == ".items[].id":
    values = [item["id"] for item in items]
elif query == '.items[] | select(.status == "mapped") | .id':
    values = [item["id"] for item in items if item["status"] == "mapped"]
elif query == '.items[] | select(.status != "mapped") | .id':
    values = [item["id"] for item in items if item["status"] != "mapped"]
else:
    match = re.fullmatch(r'.items\[\] \| select\(.id == "([a-z0-9-]+)"\) \| \.(title|level)', query)
    if match is None:
        raise ValueError("Unexpected yq expression: " + query)
    identifier, field = match.groups()
    values = [item[field] for item in items if item["id"] == identifier]
for value in values:
    print(value)
'''

PANDOC_STUB = r'''
from pathlib import Path
import sys

output = next(argument.split("=", 1)[1] for argument in sys.argv if argument.startswith("--output="))
Path(output).write_bytes(Path(sys.argv[-1]).read_bytes())
'''


class TestGenerateHtmlIndex(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        (self.root / "source").mkdir()
        (self.root / "html" / "archetypes").mkdir(parents=True)
        (self.root / "html" / "variants").mkdir()
        tools_dir = self.root / "bin"
        tools_dir.mkdir()
        for name, source in (("yq", YQ_STUB), ("pandoc", PANDOC_STUB)):
            executable = tools_dir / name
            executable.write_text(f"#!{sys.executable}\n" + source, encoding="utf-8")
            executable.chmod(0o755)
        self.environment = {**os.environ, "PATH": str(tools_dir) + os.pathsep + os.environ["PATH"]}

    def run_generator(self, items):
        (self.root / "source" / "index.yml").write_text(json.dumps({"items": items}), encoding="utf-8")
        return subprocess.run(
            ["bash", str(SCRIPT)], cwd=self.root, env=self.environment,
            text=True, capture_output=True, check=False,
        )

    def test_title_markup_is_text_in_both_sections(self):
        title = '<img src=x onerror="alert(1)"> & \'quoted\''
        for level, identifier in (("archetype", "mapped-one"), ("variant", "pending-two")):
            (self.root / "html" / (level + "s") / (identifier + ".html")).touch()
        result = self.run_generator([
            {"id": "mapped-one", "title": title, "level": "archetype", "status": "mapped"},
            {"id": "pending-two", "title": title, "level": "variant", "status": "pending"},
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        output = (self.root / "html" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<img", output)
        self.assertEqual(output.count("&lt;img"), 2)
        self.assertEqual(html.unescape(output).count(title), 2)
        self.assertIn('href="./archetypes/mapped-one.html"', output)
        self.assertIn('href="./variants/pending-two.html"', output)

    def test_echo_options_are_preserved_as_literal_titles(self):
        result = self.run_generator([
            {"id": "first", "title": "-n", "level": "archetype", "status": "mapped"},
            {"id": "second", "title": r"-e \t", "level": "variant", "status": "pending"},
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        output = (self.root / "html" / "index.html").read_text(encoding="utf-8")
        self.assertIn(">-n (Coming Soon)</span>", output)
        self.assertIn(r">-e \t (Coming Soon)</span>", output)

    def test_invalid_identifiers_fail_before_rendering(self):
        for identifier in ("../escape", 'item" onmouseover="alert(1)', "UPPER", "", "$(id)"):
            with self.subTest(identifier=identifier):
                result = self.run_generator([
                    {"id": identifier, "title": "Title", "level": "variant", "status": "mapped"},
                ])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Invalid checklist id", result.stderr)
                self.assertFalse((self.root / "html" / "index.html").exists())

    def test_invalid_index_parser_result_fails_the_pipeline(self):
        (self.root / "source" / "index.yml").write_text("invalid {", encoding="utf-8")
        result = subprocess.run(
            ["bash", str(SCRIPT)], cwd=self.root, env=self.environment,
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "html" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
