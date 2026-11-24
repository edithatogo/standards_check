"""Runtime updates must follow one exact, fail-closed dependency pin."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts import linguistic_benchmark as benchmark


class RuntimePinTests(unittest.TestCase):
    def test_pin_follows_the_exact_requirements_file(self):
        requirements = Path(benchmark.__file__).resolve().parents[1] / 'requirements/classical-nlp-reference.txt'
        self.assertEqual(benchmark.MODEL['spacy_version'], benchmark.reference_runtime_pin(requirements))
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'reference.txt'
            path.write_text('# A legitimate update\nspacy==3.8.18\n', encoding='utf-8')
            self.assertEqual(benchmark.reference_runtime_pin(path), '3.8.18')
            for content in ('spacy>=3.8.11\n', 'spacy==3.8.*\n', 'spacy==3.8.11\nspacy==3.8.18\n', '', 'spacy==3.8.11; python_version>="3.12"\n'):
                path.write_text(content, encoding='utf-8')
                with self.subTest(content=content), self.assertRaisesRegex(ValueError, 'exact spaCy pin'):
                    benchmark.reference_runtime_pin(path)
