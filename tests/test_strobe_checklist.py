import unittest
import os
import json
import shutil

from src.checklist import Checklist

class TestStrobeChecklist(unittest.TestCase):

    def setUp(self):
        """Set up test data and output file paths."""
        with open('data/strobe_cohort_checklist.json', 'r') as f:
            self.data = json.load(f)
        self.output_md = "test_strobe_checklist.md"
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
            snapshot_filename = os.path.join('tests/snapshots', f"strobe_cohort_checklist_{section.replace(' ', '_').lower()}.md")
            with open(snapshot_filename, 'r') as f:
                snapshot_content = f.read()
            self.assertEqual(markdown.strip(), snapshot_content.strip())

if __name__ == '__main__':
    unittest.main()
