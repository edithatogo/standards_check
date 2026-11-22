"""Check Make's HTML dependencies and recipe wiring without document toolchains."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


MAKEFILE = Path(__file__).resolve().parents[1] / "Makefile"
PANDOC_STUB = r'''
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("--to", choices=["html"], required=True)
parser.add_argument("--template", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--metadata", required=True)
args = parser.parse_args()
assert args.metadata.startswith("title=")
title = args.metadata.removeprefix("title=")
body = Path(args.source).read_text(encoding="utf-8")
template = Path(args.template).read_text(encoding="utf-8")
Path(args.output).write_text(template.replace("$body$", body).replace("$title$", title), encoding="utf-8")
'''


class TestMakefile(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory(prefix="standards make ")
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        shutil.copyfile(MAKEFILE, self.root / "Makefile")
        self.template = self.write(
            "templates/pandoc/html_template.html", "<title>$title$</title><main>$body$</main>",
        )
        self.write(
            "scripts/generate_html_index.sh",
            "#!/bin/sh\nmkdir -p html\nprintf 'index' > html/index.html\n",
        ).chmod(0o755)
        self.write("bin/pandoc", f"#!{sys.executable}\n" + PANDOC_STUB).chmod(0o755)
        self.environment = {**os.environ, "PATH": str(self.root / "bin") + os.pathsep + os.environ["PATH"]}

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def make(self, *arguments):
        result = subprocess.run(
            ["make", *arguments], cwd=self.root, env=self.environment,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_html_builds_english_and_legacy_sources_and_rebuilds_for_template(self):
        expected = {
            "archetypes/current.html": ("English checklist", "\n\n# English checklist"),
            "variants/extension.html": ("English extension", "# English extension"),
            "archetypes/legacy.html": ("Legacy checklist", "# Legacy checklist"),
        }
        sources = [
            self.write("markdown/en/archetypes/current.md", expected["archetypes/current.html"][1]),
            self.write("markdown/en/variants/extension.md", expected["variants/extension.html"][1]),
            self.write("markdown/archetypes/legacy.md", expected["archetypes/legacy.html"][1]),
            self.write("markdown/archetypes/current.md", "# Superseded legacy checklist"),
        ]
        baseline = 1_600_000_000
        for path in [self.template, *sources]:
            os.utime(path, (baseline, baseline))

        self.make("html")
        for relative, (title, body) in expected.items():
            output = self.root / "html" / relative
            self.assertEqual(
                output.read_text(encoding="utf-8"), f"<title>{title}</title><main>{body}</main>",
            )
            os.utime(output, (baseline + 1, baseline + 1))
        self.assertEqual((self.root / "html/index.html").read_text(encoding="utf-8"), "index")

        self.template.write_text("<title>$title$</title><article>$body$</article>", encoding="utf-8")
        os.utime(self.template, (baseline + 2, baseline + 2))
        self.make("html")
        for relative, (title, body) in expected.items():
            self.assertEqual(
                (self.root / "html" / relative).read_text(encoding="utf-8"),
                f"<title>{title}</title><article>{body}</article>",
            )

    def test_citations_run_once_without_duplicate_recipe_warnings(self):
        for target in ("build", "citations"):
            with self.subTest(target=target):
                self.assertEqual(self.make("-n", target).count("bash scripts/generate_citations.sh"), 1)


if __name__ == "__main__":
    unittest.main()
