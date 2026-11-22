import unittest
import os
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from src.checklist import Checklist

class TestChecklist(unittest.TestCase):

    def setUp(self):
        """Set up test data and output file paths."""
        with open('data/consort_checklist.json', 'r') as f:
            self.data = json.load(f)
        self.output_md = "test_checklist.md"
        self.checklist = Checklist(self.data)

    def tearDown(self):
        """Remove generated files after each test."""
        if os.path.exists(self.output_md):
            shutil.rmtree(self.output_md)

    def test_generate_checklist_md(self):
        """Test that the checklist is generated as a Markdown file."""
        self.checklist.generate(self.output_md)
        self.assertTrue(os.path.exists(self.output_md))

    def test_snapshot(self):
        """Test that the generated markdown matches the snapshot."""
        sections = self.checklist.to_markdown_by_section()
        for section, markdown in sections.items():
            snapshot_filename = os.path.join('tests/snapshots', f"consort_checklist_{section.replace(' ', '_').lower()}.md")
            with open(snapshot_filename, 'r') as f:
                snapshot_content = f.read()
            self.assertEqual(markdown.strip(), snapshot_content.strip())

    def test_all_response_types(self):
        items = [{'section': 'Methods', 'id': kind, 'description': kind,
                  'type': kind, 'options': ['First', 'Second']}
                 for kind in ('boolean', 'string', 'integer', 'multiple_choice')]
        markdown = Checklist({'items': items}).to_markdown()
        self.assertIn('[ ] Yes\n[ ] No', markdown)
        self.assertEqual(markdown.count('Response: ________________'), 2)
        self.assertIn('[ ] First\n[ ] Second', markdown)

    def test_unsafe_or_colliding_sections_do_not_write_files(self):
        for sections in (['../outside'], ['..\\outside'], ['A B', 'A_B']):
            with self.subTest(sections=sections), TemporaryDirectory() as directory:
                items = [{'section': section, 'id': '1', 'description': 'Example',
                          'type': 'boolean'} for section in sections]
                output = Path(directory) / 'checklist'
                with self.assertRaises(ValueError):
                    Checklist({'items': items}).generate(output)
                self.assertFalse(output.exists())

if __name__ == '__main__':
    unittest.main()
