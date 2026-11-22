import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree

from jsonschema import ValidationError

from src.main import generate_artifact, validate_data

ROOT = Path(__file__).resolve().parent.parent


class TestMain(unittest.TestCase):
    def test_all_canonical_fixtures_validate_and_generate(self):
        with TemporaryDirectory() as directory:
            for fixture in sorted((ROOT / 'data').glob('*.json')):
                with self.subTest(fixture=fixture.name):
                    data = json.loads(fixture.read_text())
                    if fixture.name.startswith('invalid_'):
                        with self.assertRaises(ValidationError):
                            validate_data(data)
                        continue
                    validate_data(data)
                    suffix = '.svg' if 'diagram_type' in data else '.md'
                    output = Path(directory) / (fixture.stem + suffix)
                    generate_artifact(fixture, output)
                    self.assertGreater(output.stat().st_size, 0)
                    if suffix == '.svg':
                        self.assertTrue(ElementTree.parse(output).findall(
                            './/{http://www.w3.org/2000/svg}text'))
                    else:
                        self.assertIn(data['items'][0]['description'], output.read_text())

    def test_prisma_counts_use_remaining_records(self):
        data = {
            'diagram_type': 'PRISMA', 'records_identified': 150,
            'records_after_duplicates_removed': 130, 'records_screened': 130,
            'records_excluded': 30, 'full_text_articles_assessed': 100,
            'full_text_articles_excluded': 10, 'studies_included': 90,
            'databases': 100, 'registers': 50, 'duplicates': 20,
        }
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'counts.svg'
            generate_artifact(data, output)
            labels = [element.text for element in ElementTree.parse(output).findall(
                './/{http://www.w3.org/2000/svg}text')]
            self.assertEqual(labels.count('(n = 130)'), 2)
            self.assertNotIn('(n = 20)', labels)

    def test_discriminator_and_override_errors_do_not_write(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'invalid.svg'
            for data in ({}, {'diagram_type': 'UNKNOWN'},
                         {'diagram_type': []},
                         {'diagram_type': 'PRISMA', 'checklist_type': 'CARE'}):
                with self.subTest(data=data):
                    with self.assertRaises(ValueError):
                        generate_artifact(data, output)
                    self.assertFalse(output.exists())
            for override in ('missing-equals', '=123', 'records_screened=-1'):
                with self.subTest(override=override):
                    with self.assertRaises((ValueError, ValidationError)):
                        generate_artifact(ROOT / 'data/prisma_data.json', output,
                                          set_values=[override])
                    self.assertFalse(output.exists())

    def test_checklist_single_file_and_legacy_directory(self):
        with TemporaryDirectory() as directory:
            fixture = ROOT / 'data/care_checklist.json'
            output = Path(directory) / 'care.md'
            generate_artifact(fixture, output)
            self.assertTrue(output.is_file())
            section_directory = Path(directory) / 'care'
            generate_artifact(fixture, section_directory)
            self.assertTrue(list(section_directory.glob('*.md')))
            with self.assertRaises(ValueError):
                generate_artifact(fixture, Path(directory) / 'care.typ')


if __name__ == '__main__':
    unittest.main()
