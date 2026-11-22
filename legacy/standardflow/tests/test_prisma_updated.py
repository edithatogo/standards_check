import unittest
import os
import json

from src.prisma import PrismaDiagram

class TestPrismaUpdated(unittest.TestCase):

    def setUp(self):
        """Set up test data and output file paths."""
        with open('data/prisma_2020_updated_data.json', 'r') as f:
            self.data = json.load(f)
        self.output_png = "test_prisma_updated.png"
        self.snapshot_file = "tests/snapshots/prisma_updated.dot"
        self.prisma = PrismaDiagram(self.data)

    def tearDown(self):
        """Remove generated files after each test."""
        if os.path.exists(self.output_png):
            os.remove(self.output_png)
            if os.path.exists(os.path.splitext(self.output_png)[0]):
                os.remove(os.path.splitext(self.output_png)[0])

    def test_generate_prisma_updated_diagram_png(self):
        """Test that the updated PRISMA diagram is generated as a PNG file."""
        self.prisma.generate(self.output_png)
        self.assertTrue(os.path.exists(self.output_png))

    def test_snapshot(self):
        """Test that the generated dot source matches the snapshot."""
        self.prisma._build_graph()
        generated_dot = self.prisma.dot.source
        with open(self.snapshot_file, 'r') as f:
            snapshot_dot = f.read()
        self.assertEqual(generated_dot.strip(), snapshot_dot.strip())

if __name__ == '__main__':
    unittest.main()
