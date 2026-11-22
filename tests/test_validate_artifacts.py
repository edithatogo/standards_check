"""The SVG accessibility gate must check the generated scene's actual DOM."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts import validate_artifacts


class TestValidateArtifacts(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.stem = "new-databases-registers"
        for extension in ("svg", "txt", "scene.json"):
            filename = f"{self.stem}.{extension}"
            shutil.copyfile(validate_artifacts.GENERATED / filename, self.root / filename)
        pack = self.root / "packs/org.prisma/prisma/2020/pack.json"
        pack.parent.mkdir(parents=True)
        pack.touch()
        self.svg = self.root / f"{self.stem}.svg"
        self.original = self.svg.read_text(encoding="utf-8")
        self.namespace = {"svg": "http://www.w3.org/2000/svg"}

    def validate(self):
        with patch.multiple(
            validate_artifacts, ROOT=self.root, GENERATED=self.root,
            VARIANTS={self.stem: validate_artifacts.VARIANTS[self.stem]},
        ), patch("sys.argv", ["validate_artifacts.py"]), redirect_stdout(io.StringIO()):
            validate_artifacts.main()

    def assert_rejected(self, root, diagnostic):
        self.svg.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        errors = io.StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit) as result:
            self.validate()
        self.assertEqual(result.exception.code, 1)
        self.assertIn(diagnostic, errors.getvalue())

    def test_existing_scene_referenced_fixture_passes(self):
        self.validate()

    def test_aria_targets_must_resolve_to_the_title_and_description(self):
        for selector in ("svg:title", "svg:desc"):
            with self.subTest(selector=selector):
                root = ET.fromstring(self.original)
                root.find(selector, self.namespace).set("id", "wrong-id")
                self.assert_rejected(root, "must resolve")

    def test_duplicate_aria_target_ids_fail(self):
        root = ET.fromstring(self.original)
        ET.SubElement(root, "{http://www.w3.org/2000/svg}g", id="standardflow-title")
        self.assert_rejected(root, "must resolve")

    def test_every_list_item_needs_a_nonempty_label(self):
        for label in (None, " "):
            with self.subTest(label=label):
                root = ET.fromstring(self.original)
                nodes = root.findall(".//svg:g[@role='listitem']", self.namespace)
                if label is None:
                    nodes[-1].attrib.pop("aria-label")
                else:
                    nodes[-1].set("aria-label", label)
                self.assert_rejected(root, "labelled list-item nodes")

    def test_svg_dom_order_must_match_the_scene_reading_order(self):
        root = ET.fromstring(self.original)
        collection = root.find(".//svg:g[@role='list']", self.namespace)
        collection[:] = list(reversed(collection))
        self.assert_rejected(root, "reading order differs")


if __name__ == "__main__":
    unittest.main()
