import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import extractive_development as e


class SpanTests(unittest.TestCase):
    def test_rules_find_full_spans_not_just_cue_words(self):
        text = 'For trials, report A unless exempt.'
        self.assertEqual([(k, text[a:b]) for k, a, b in e.rules(text)],
                         [('applicability', 'For trials'), ('exception', 'unless exempt')])
        self.assertEqual(e.rules('If.'), [])
        self.assertEqual(e.rules('Report the reason for exclusion.'), [])

    def test_reference_labels_require_unique_exact_source_span(self):
        for labels in [[['bad', 'x']], [['condition', 'x']], [['condition', '']],
                       [['condition', 'xx'], ['condition', 'xx']]]:
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                e.references({'text': 'xx xx' if len(labels) == 1 else 'xx', 'labels': labels})

    def test_offsets_roundtrip_confidence_and_duplicates(self):
        good = {'start': 0, 'end': 4, 'text': 'If A', 'confidence': .9}
        self.assertEqual(e.model_spans('If A', {'entities': {'condition': [good, good]}}),
                         [('condition', 0, 4), ('condition', 0, 4)])
        for bad in [None, {}, {'entities': {'bogus': []}}, {'entities': {'condition': 'x'}},
                    {'entities': {'condition': [None]}},
                    {'entities': {'condition': [{**good, 'start': True}]}},
                    {'entities': {'condition': [{**good, 'end': 9}]}},
                    {'entities': {'condition': [{**good, 'text': 'If B'}]}},
                    {'entities': {'condition': [{**good, 'confidence': float('nan')}]}},
                    {'entities': {'condition': [{**good, 'confidence': 2}]}},
                    {'entities': {'condition': [{**good, 'confidence': '0.9'}]}}]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                e.model_spans('If A', bad)

    def test_eval_keeps_duplicates_and_invalid_output_in_denominator(self):
        cases = [{'id':'a','family':'one','text':'If A','labels':[['condition','If A']]},
                 {'id':'b','family':'two','text':'Unless B','labels':[['exception','Unless B']]}]
        model = Mock()
        model.extract_entities.side_effect = [
            {'entities': {'condition': [{'start':0,'end':4,'text':'If A','confidence':.9}]*2}},
            {'entities': {'exception': [{'start':1,'end':8,'text':'Unless B','confidence':.9}]}},
        ]
        result = e.evaluate(cases, e.model_predictor(model))
        self.assertEqual(result['scores']['all']['tp'], 1)
        self.assertEqual(result['scores']['all']['fp'], 1)
        self.assertEqual(result['scores']['all']['fn'], 1)
        self.assertEqual(result['invalid_abstentions'], 1)
        self.assertEqual(result['missed_qualifiers'], 1)
        self.assertEqual(model.extract_entities.call_args.kwargs['overlap_policy'], 'allow')


@unittest.skipUnless(sys.platform.startswith('linux'), 'RSS receipt is Linux-specific')
class RuntimeTests(unittest.TestCase):
    def test_rules_arm_receipt_and_fixture_pin(self):
        result = e.run('rules', None, 'test')
        self.assertEqual(result['scores']['all']['tp'], 14)
        self.assertEqual(result['scores']['all']['fp'], 2)
        self.assertEqual(result['scores']['all']['fn'], 3)
        self.assertEqual(len(result['cases']), 16)
        self.assertFalse(result['scientific_qualification'])
        self.assertEqual(result['canonical_packs_promoted'], 0)
        with patch.object(e, 'FIXTURE_SHA256', 'wrong'), self.assertRaisesRegex(ValueError, 'fixture bytes'):
            e.run('rules', None, 'test')
        with self.assertRaisesRegex(ValueError, 'unsupported arm'):
            e.run('unknown', None, 'test')

    def test_model_loader_rejects_unpinned_runtime_and_weights(self):
        with patch.object(e, 'version', return_value='wrong'), self.assertRaisesRegex(ValueError, 'runtime'):
            e.load_model(Path('.'))
        with tempfile.TemporaryDirectory() as directory, patch.object(e, 'version', side_effect=e.RUNTIME.get):
            root = Path(directory)
            for name in e.ASSETS:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'test')
            with self.assertRaisesRegex(ValueError, 'unqualified model weights'):
                e.load_model(root)
            # Test actual local boundary with fakes; no inference claim.
            from hashlib import sha256
            fake = Mock()
            fake.extract_entities.return_value = {'entities': {}}
            torch = Mock()
            gliner = SimpleNamespace(AutoExtractor=SimpleNamespace(from_pretrained=Mock(return_value=fake)))
            with patch.object(e, 'MODEL_SHA256', sha256(b'test').hexdigest()), patch.object(e, 'MODEL_BYTES', 4), patch.dict(sys.modules, {'torch':torch, 'gliner2':gliner}):
                result = e.run('gliner', root, 'test')
                self.assertEqual(result['scores']['all']['fn'], 17)
                self.assertEqual(result['model_weight_bytes'], 4)
                gliner.AutoExtractor.from_pretrained.assert_called_once_with(str(root), map_location='cpu', local_files_only=True)
                fake.eval.assert_called_once()

    def test_cli_retains_failure_and_success(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'result.json'
            argv = ['extractive_development','--arm','rules','--revision','test','--output',str(output)]
            with patch.object(sys, 'argv', argv):
                e.main()
            self.assertEqual(json.loads(output.read_text())['scores']['all']['tp'], 14)
            with patch.object(sys, 'argv', argv), patch.object(e, 'run', side_effect=ValueError('held')), self.assertRaises(SystemExit):
                e.main()
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt['status'], 'failed')
            self.assertFalse(receipt['scientific_qualification'])
