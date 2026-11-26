import unittest
from unittest.mock import Mock
from scripts import tagger_followup as t


class TaggerFollowupTests(unittest.TestCase):
    def test_folds_exclude_entire_stratum_and_evaluate_every_case(self):
        cases = t.cases_from_fixture()
        folds = t.folds(cases)
        self.assertEqual(len(folds), 3)
        self.assertEqual({x['id'] for _, _, test in folds for x in test}, {c['id'] for c in cases})
        for family, train, test in folds:
            self.assertNotIn(family, {c['family'] for c in train})
            self.assertEqual({c['family'] for c in test}, {family})
        result = t.supervised(cases)
        for arm in result['arms'].values():
            self.assertEqual(len(arm['cases']), 16)
            self.assertEqual(arm['scores']['all']['tp'] + arm['scores']['all']['fn'], 17)

    def test_token_boundaries_and_overlap_across_types(self):
        text = 'If A (unless B), report C.'
        case = {'text':text, 'labels':[['condition','If A (unless B)'],['exception','unless B']]}
        words = t.tokens(text)
        cond = t.bio_labels(words, case, 'condition')
        exc = t.bio_labels(words, case, 'exception')
        self.assertEqual(t.decode_bio(words, cond, 'condition'), [('condition',0,15)])
        self.assertEqual(t.decode_bio(words, exc, 'exception'), [('exception',6,14)])
        self.assertEqual(t.decode_bio(words, ['I']+['O']*(len(words)-1), 'condition'), [('condition',0,2)])
        with self.assertRaises(ValueError):
            t.bio_labels(words, {'text':text,'labels':[['condition','I']]}, 'condition')

    def test_label_framing_preserves_source_validation_and_distinct_calls(self):
        fake = Mock()
        fake.extract_entities.side_effect = [ {'entities':{k:[]}} for k in t.e.LABELS]
        observed, raw = t.framed_predictor(fake, 'per_type')('If A')
        self.assertEqual(observed, [])
        self.assertEqual(fake.extract_entities.call_count, 3)
        self.assertEqual(set(raw['entities']), set(t.e.LABELS))
        fake.reset_mock(side_effect=True)
        fake.extract_entities.return_value = {'entities': {'condition':[{'start':0,'end':4,'text':'If A','confidence':.9}]}}
        self.assertEqual(t.framed_predictor(fake,'clause')('If A')[0],[('condition',0,4)])
        with self.assertRaises(ValueError): t.framed_predictor(fake,'other')

    def test_nb_rejects_empty_and_untrained(self):
        model = t.NB()
        with self.assertRaises(ValueError): model.fit([])
        with self.assertRaises(ValueError): model.predict(['a'])

    def test_invalid_input_and_supervised_positive_path(self):
        from unittest.mock import patch
        cases = t.cases_from_fixture()
        with patch.object(t.e, 'FIXTURE_SHA256', 'bad'), self.assertRaises(ValueError):
            t.cases_from_fixture()
        with self.assertRaises(ValueError): t.folds([cases[0], cases[0]])
        with self.assertRaises(ValueError): t.folds([cases[0]])
        with self.assertRaises(ValueError): t.fit_models(cases, 'invalid')
        case = {'text':'If A B', 'labels':[['condition','If A'],['condition','A B']]}
        with self.assertRaises(ValueError): t.bio_labels(t.tokens(case['text']), case, 'condition')
        fake = Mock()
        fake.distribution.return_value = {'yes':1.0}
        self.assertEqual(t.predict_supervised('If A', {'condition':fake}, 'span_boundary'), [('condition',0,2),('condition',3,4)])
        fake.extract_entities.return_value = {'entities': {'exception': []}}
        with self.assertRaises(ValueError): t.framed_predictor(fake,'per_type')('If A')

    @unittest.skipUnless(__import__('sys').platform.startswith('linux'), 'Linux RSS receipt')
    def test_cli_receipt_and_failed_loader(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'out.json'
            argv = ['tagger_followup','--arm','supervised','--revision','test','--output',str(path)]
            with patch('sys.argv', argv): t.main()
            self.assertEqual(json.loads(path.read_text())['arms']['rules']['scores']['all']['tp'],14)
            argv[2] = 'clause'
            fake = Mock()
            fake.extract_entities.return_value = {'entities': {}}
            with patch('sys.argv', argv), patch.object(t.e,'load_extractor',return_value=(fake,{},{})):
                t.main()
            self.assertEqual(json.loads(path.read_text())['evaluation']['scores']['all']['fn'],17)
            with patch('sys.argv', argv), patch.object(t.e,'load_extractor',side_effect=ValueError('held')), self.assertRaises(SystemExit):
                t.main()
            self.assertEqual(json.loads(path.read_text())['status'],'failed')

    def test_shared_loader_preserves_predictor_factory(self):
        from unittest.mock import patch
        extractor = Mock()
        predictor = Mock()
        factory = Mock(return_value=predictor)
        with patch.object(t.e, 'load_extractor', return_value=(extractor, {'runtime': 'test'}, {'asset': 'test'})):
            loaded, runtime, assets = t.e.load_model(None, predictor_factory=factory)
        factory.assert_called_once_with(extractor)
        self.assertIs(loaded, predictor)
        self.assertEqual(runtime, {'runtime': 'test'})
        self.assertEqual(assets, {'asset': 'test'})
