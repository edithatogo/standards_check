import unittest
import os
import json

from src.prisma import PrismaDiagram
from jsonschema import ValidationError

class TestPrisma(unittest.TestCase):

    def setUp(self):
        """Set up test data and output file paths."""
        self.valid_data = {
            "diagram_type": "PRISMA",
            "records_identified": 1000,
            "records_after_duplicates_removed": 800,
            "records_screened": 800,
            "records_excluded": 200,
            "full_text_articles_assessed": 600,
            "full_text_articles_excluded": 300,
            "studies_included": 300
        }
        self.invalid_data = {
            "diagram_type": "PRISMA",
            "records_identified": "invalid_data",
            "records_after_duplicates_removed": 800,
            "records_screened": 800,
            "records_excluded": 200,
            "full_text_articles_assessed": 600,
            "full_text_articles_excluded": 300,
            "studies_included": 300
        }
        self.output_png = "test_prisma.png"
        self.output_svg = "test_prisma.svg"
        self.output_pdf = "test_prisma.pdf"
        self.output_tiff = "test_prisma.tiff"
        self.output_eps = "test_prisma.eps"
        self.prisma = PrismaDiagram(self.valid_data)

    def tearDown(self):
        """Remove generated files after each test."""
        for f in [self.output_png, self.output_svg, self.output_pdf, self.output_tiff, self.output_eps]:
            if os.path.exists(f):
                # We need to also remove the source file for some formats
                if os.path.splitext(f)[1] in ['.eps', '.pdf', '.svg', '.png']:
                    if os.path.exists(os.path.splitext(f)[0]):
                        os.remove(os.path.splitext(f)[0])
                os.remove(f)


    def test_generate_prisma_diagram_png(self):
        """Test that the PRISMA diagram is generated as a PNG file."""
        self.prisma.generate(self.output_png)
        self.assertTrue(os.path.exists(self.output_png))

    def test_generate_prisma_diagram_svg(self):
        """Test that the PRISMA diagram is generated as an SVG file."""
        self.prisma.generate(self.output_svg)
        self.assertTrue(os.path.exists(self.output_svg))

    def test_generate_prisma_diagram_pdf(self):
        """Test that the PRISMA diagram is generated as a PDF file."""
        self.prisma.generate(self.output_pdf)
        self.assertTrue(os.path.exists(self.output_pdf))

    def test_generate_prisma_diagram_tiff(self):
        """Test that the PRISMA diagram is generated as a TIFF file."""
        self.prisma.generate(self.output_tiff)
        self.assertTrue(os.path.exists(self.output_tiff))

    def test_generate_prisma_diagram_eps(self):
        """Test that the PRISMA diagram is generated as an EPS file."""
        self.prisma.generate(self.output_eps)
        self.assertTrue(os.path.exists(self.output_eps))

    def test_snapshot(self):
        """Test that the generated dot source matches the snapshot."""
        self.snapshot_file = "tests/snapshots/prisma.dot"
        self.prisma._build_graph()
        generated_dot = self.prisma.dot.source
        with open(self.snapshot_file, 'r') as f:
            snapshot_dot = f.read()
        self.assertEqual(generated_dot.strip(), snapshot_dot.strip())


if __name__ == '__main__':
    unittest.main()
