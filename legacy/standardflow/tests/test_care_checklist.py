import unittest
import os
import json
from src.checklist import Checklist

class TestCareChecklist(unittest.TestCase):

    def setUp(self):
        with open('data/care_checklist.json', 'r') as f:
            self.data = json.load(f)
        self.checklist = Checklist(self.data)

    def test_snapshot(self):
        markdown = self.checklist.to_markdown()
        snapshot_filename = os.path.join('tests/snapshots', 'care_checklist.md')
        with open(snapshot_filename, 'r') as f:
            snapshot_content = f.read()
        self.assertEqual(markdown.strip(), snapshot_content.strip())

if __name__ == '__main__':
    unittest.main()
