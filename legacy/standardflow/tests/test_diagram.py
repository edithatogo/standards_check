import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

from src.consort import ConsortDiagram
from src.prisma import PrismaDiagram
from src.strobe import StrobeDiagram


class TestDiagram(unittest.TestCase):
    def test_variants_render_labelled_svg(self):
        cases = (
            ('prisma', PrismaDiagram, 'Records screened', '800'),
            ('prisma_2020_updated', PrismaDiagram, 'previous version', '160'),
            ('consort', ConsortDiagram, 'Allocated to intervention', '400'),
            ('consort_cluster', ConsortDiagram, 'clusters', 'individuals'),
            ('strobe', StrobeDiagram, 'Included in study', '720'),
            ('strobe_cohort', StrobeDiagram, 'Exposed Group', 'Unexposed Group'),
        )
        with TemporaryDirectory() as directory:
            for name, renderer, label, count in cases:
                with self.subTest(name=name):
                    data = json.loads(Path(f'data/{name}_data.json').read_text())
                    output = Path(directory) / f'{name}.svg'
                    renderer(data).generate(output)
                    texts = ElementTree.parse(output).findall(
                        './/{http://www.w3.org/2000/svg}text')
                    rendered = ' '.join(text.text or '' for text in texts)
                    self.assertIn(label, rendered)
                    self.assertIn(count, rendered)

    def test_styles_and_typst_reference(self):
        data = json.loads(Path('data/prisma_data.json').read_text())
        data['style'] = {
            'box_color': '#ffff00', 'font_color': '#ff0000',
            'font_name': 'Helvetica', 'font_size': '16',
            'arrow_color': '#0000ff',
        }
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'diagram.typ'
            diagram = PrismaDiagram(data)
            diagram.generate(output)
            self.assertEqual(output.read_text(), '#image("diagram.svg")\n')
            svg = output.with_suffix('.svg').read_text()
            for value in ('#ffff00', '#ff0000', '#0000ff', 'Helvetica', '16.00'):
                self.assertIn(value, svg)
            self.assertIn('Records screened', svg)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()),
                             ['diagram.svg', 'diagram.typ'])

    def test_tiff_failure_keeps_existing_png(self):
        data = json.loads(Path('data/prisma_data.json').read_text())
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'diagram.tiff'
            png = output.with_suffix('.png')
            png.write_bytes(b'existing user output')
            with patch('src.diagram.subprocess.run',
                       side_effect=subprocess.CalledProcessError(1, ['convert'])):
                with self.assertRaises(subprocess.CalledProcessError):
                    PrismaDiagram(data).generate(output)
            self.assertEqual(png.read_bytes(), b'existing user output')
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
