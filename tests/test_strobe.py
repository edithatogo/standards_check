import unittest
import os
import json

from src.strobe import StrobeDiagram

class TestStrobe(unittest.TestCase):

    def setUp(self):
        """Set up test data and output file paths."""
        with open('data/strobe_data.json', 'r') as f:
            self.data = json.load(f)
        self.output_png = "test_strobe.png"
        self.strobe = StrobeDiagram(self.data)

    def tearDown(self):
        """Remove generated files after each test."""
        if os.path.exists(self.output_png):
            os.remove(self.output_png)
            if os.path.exists(os.path.splitext(self.output_png)[0]):
                os.remove(os.path.splitext(self.output_png)[0])

    def test_generate_strobe_diagram_png(self):
        """Test that the STROBE diagram is generated as a PNG file."""
        self.strobe.generate(self.output_png)
        self.assertTrue(os.path.exists(self.output_png))

    def test_snapshot(self):
        """Test that the generated dot source matches the snapshot."""
        self.snapshot_file = "tests/snapshots/strobe.dot"
        self.strobe._build_graph()
        generated_dot = self.strobe.dot.source
        with open(self.snapshot_file, 'r') as f:
            snapshot_dot = f.read()
        self.assertEqual(generated_dot.strip(), snapshot_dot.strip())

if __name__ == '__main__':
    unittest.main()
