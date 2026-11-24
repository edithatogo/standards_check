import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.linguistic_benchmark import evaluate, metrics, mutate, pinned_model, SYNTHETIC


class BenchmarkTests(unittest.TestCase):
    def test_metrics_keep_abstentions_and_false_acceptance_visible(self):
        rows = [
            {'expected': ['negation'], 'observed': ['negation', 'roles'], 'held': False},
            {'expected': ['roles'], 'observed': [], 'held': False},
            {'expected': [], 'observed': ['logic'], 'held': False},
            {'expected': ['modality'], 'observed': [], 'held': True},
        ]
        m = metrics(rows)
        self.assertEqual((m['tp'], m['fp'], m['fn']), (1, 2, 2))
        self.assertEqual(m['held'], 1)
        self.assertEqual(m['material_no_signal'], 1)
        self.assertEqual(m['material_held'], 1)
        self.assertEqual(m['control_false_alert'], 1)
        self.assertAlmostEqual(m['precision'], 1/3)
        self.assertAlmostEqual(m['recall'], 1/3)
        self.assertIsNone(metrics([])['precision'])

    def test_frozen_synthetic_suite_and_privacy(self):
        result = evaluate(SYNTHETIC)
        self.assertEqual(len(result['cases']), len(SYNTHETIC))
        self.assertEqual(result['canonical_packs_promoted'], 0)
        self.assertGreater(result['metrics']['tp'], 0)
        self.assertNotIn('The nurse', str(result))
        self.assertEqual(result['groups']['synthetic']['cases'], len(SYNTHETIC))

    def test_source_mutation_must_be_unique(self):
        self.assertEqual(mutate('Report all outcomes.', 'all', 'some'), 'Report some outcomes.')
        for text in ('Report outcomes.', 'Report all outcomes and all harms.'):
            with self.assertRaises(ValueError):
                mutate(text, 'all', 'some')

    def test_model_rejects_wrong_bytes_before_loading(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'model.whl'
            path.write_bytes(b'not model bytes')
            with patch('scripts.linguistic_benchmark.load_reference') as loader:
                with self.assertRaisesRegex(ValueError, 'wheel'):
                    with pinned_model(path):
                        self.fail('untrusted model loaded')
                loader.assert_not_called()

    def test_case_validation_and_no_comparison_false_signal(self):
        with self.assertRaises(ValueError):
            evaluate([('x', '1', 'A', 'B', ['not-a-field'])])
        with self.assertRaises(ValueError):
            evaluate([('x', '1', 'A', 'B', []), ('x', '1', 'A', 'B', [])])
        r = evaluate([('x', '1', '', 'Report A.', ['roles'])])
        self.assertEqual(r['metrics']['material_held'], 1)
        self.assertEqual(r['metrics']['material_no_signal'], 0)

    def test_cli_reports_synthetic_fixture_identity(self):
        import json
        from scripts.linguistic_benchmark import main
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / 'evidence' / 'report.json'
            with patch('sys.argv', ['benchmark', '--synthetic-only', '--output', str(out)]):
                main()
            report = json.loads(out.read_text())
            self.assertEqual(report['method'], 'rules')
            self.assertEqual(len(report['fixture_sha256']), 64)
            self.assertIsNone(report['model'])

    def test_verified_wheel_path_and_reference_metadata_guards(self):
        import hashlib
        from types import SimpleNamespace
        from zipfile import ZipFile
        from scripts.linguistic_benchmark import MODEL
        with TemporaryDirectory() as tmp:
            wheel = Path(tmp) / 'fixture.whl'
            with ZipFile(wheel, 'w') as archive:
                archive.writestr('en_core_web_sm/en_core_web_sm-3.8.0/meta.json', '{}')
            raw = wheel.read_bytes()
            pin = {**MODEL, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            model = SimpleNamespace(meta={'license': 'MIT', 'name': 'core_web_sm'})
            ref = {'spacy_version': MODEL['spacy_version'], 'model_version': MODEL['version']}
            def loader(path):
                self.assertTrue((path / 'meta.json').is_file())
                return model, ref
            with patch('scripts.linguistic_benchmark.MODEL', pin), patch('scripts.linguistic_benchmark.load_reference', side_effect=loader):
                with pinned_model(wheel) as selected:
                    self.assertIs(selected, model)
                model.meta['license'] = 'wrong'
                with self.assertRaisesRegex(ValueError, 'licence'):
                    with pinned_model(wheel):
                        self.fail('wrong licence accepted')
                ref['model_version'] = 'wrong'
                with self.assertRaisesRegex(ValueError, 'version'):
                    with pinned_model(wheel):
                        self.fail('wrong version accepted')

    def test_actual_retained_source_cases_when_checkout_available(self):
        from scripts.linguistic_benchmark import source_cases
        root = Path(__file__).resolve().parents[1]
        if not (root / 'source/official/authoritative-article-rows.json').is_file():
            self.skipTest('isolated local module tests, source ledger absent')
        cases, pins = source_cases(root)
        self.assertEqual(len(cases), 16)
        self.assertEqual(set(pins), {'prisma-s-2021', 'cheers-2022'})
        report = evaluate(cases)
        self.assertEqual(set(report['groups']), {'PRISMA', 'CHEERS'})
        self.assertEqual(report['metrics']['held'], 0)
