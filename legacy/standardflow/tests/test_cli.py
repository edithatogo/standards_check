import json
from pathlib import Path
import os
import subprocess
import sys
import unittest

from click.testing import CliRunner

from src.cli import cli

ROOT = Path(__file__).resolve().parent.parent


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_list_and_schemas(self):
        for args, expected in (
            (['list'], 'CONSORT_CLUSTER'), (['list'], 'CARE'),
            (['schemas'], 'CHECKLIST'),
            (['schemas', 'consort'], 'CONSORT 2010 flow diagram schema'),
        ):
            with self.subTest(args=args):
                result = self.runner.invoke(cli, args)
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn(expected, result.output)
        result = self.runner.invoke(cli, ['schemas', '../requirements'])
        self.assertNotEqual(result.exit_code, 0)

    def test_generation_from_another_directory_and_default_png(self):
        with self.runner.isolated_filesystem():
            for output in ('diagram.png', 'diagram.svg', 'diagram.pdf', 'diagram.typ'):
                with self.subTest(output=output):
                    result = self.runner.invoke(cli, [
                        'generate', str(ROOT / 'data/prisma_data.json'), '-o', output,
                    ])
                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertGreater(Path(output).stat().st_size, 0)
            result = self.runner.invoke(cli, [
                'generate', str(ROOT / 'data/prisma_data.json'),
            ])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(Path('output.png').read_bytes().startswith(b'\x89PNG'))

    def test_validate_returns_nonzero_for_invalid_data(self):
        with self.runner.isolated_filesystem():
            for contents in ('{', '[]', '{}', '{"diagram_type": "CONSORT"}'):
                with self.subTest(contents=contents):
                    Path('invalid.json').write_text(contents)
                    result = self.runner.invoke(cli, ['validate', 'invalid.json'])
                    self.assertNotEqual(result.exit_code, 0)
                    self.assertIn('Validation failed:', result.output)
            for fixture in ('prisma_data.json', 'care_checklist.json'):
                result = self.runner.invoke(cli, ['validate', str(ROOT / 'data' / fixture)])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn('Validation successful!', result.output)

    def test_style_and_overrides_reach_the_rendered_output(self):
        with self.runner.isolated_filesystem():
            Path('style.json').write_text(json.dumps({'box_color': '#ff0000'}))
            result = self.runner.invoke(cli, [
                'generate', str(ROOT / 'data/prisma_data.json'), '-o', 'styled.svg',
                '--style', 'style.json', '--set', 'records_screened=777',
            ])
            self.assertEqual(result.exit_code, 0, result.output)
            svg = Path('styled.svg').read_text()
            self.assertIn('#ff0000', svg)
            self.assertIn('(n = 777)', svg)

    def test_legacy_module_entrypoint(self):
        with self.runner.isolated_filesystem():
            result = subprocess.run(
                [sys.executable, '-m', 'src', str(ROOT / 'data/prisma_data.json'),
                 '-o', 'module.svg'],
                env={**os.environ, 'PYTHONPATH': str(ROOT)},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('<svg', Path('module.svg').read_text())


if __name__ == '__main__':
    unittest.main()
