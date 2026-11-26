import unittest
from qualifier_frames import schema, predictor_factory


class FrameTests(unittest.TestCase):
    def test_all_three_canonical_types_and_fixed_frames(self):
        for frame in ('clause-names', 'operator-first'):
            labels, mapping = schema(frame)
            self.assertEqual(set(labels),set(mapping))
            self.assertEqual(set(mapping.values()),{'applicability','condition','exception'})
            self.assertEqual(len(labels),3)
        with self.assertRaises(ValueError):
            schema('unknown')

    def test_alias_mapping_preserves_source_spans_and_raw_response(self):
        labels, mapping = schema('clause-names')
        alias = next(k for k,v in mapping.items() if v=='condition')
        raw = {'entities':{alias:[{'start':0,'end':5,'text':'If so','confidence':.9}]}}
        class Model:
            def extract_entities(self,text,request,**kwargs):
                assert text=='If so, act.' and request==labels
                assert kwargs=={'include_spans':True,'include_confidence':True,'threshold':.5,'overlap_policy':'allow'}
                return raw
        def validate(text,response):
            self.assertEqual(response['entities'],{'condition':raw['entities'][alias]})
            return [('condition',0,5)]
        predict = predictor_factory('clause-names',validate)(Model())
        self.assertEqual(predict('If so, act.'),([('condition',0,5)],raw))

    def test_invalid_response_fails_closed(self):
        class Model:
            def extract_entities(self,*a,**kw): return {'entities':{'unrequested':[]}}
        def validate(*a): self.fail('unknown alias must not reach validation')
        with self.assertRaisesRegex(ValueError,'unrequested'):
            predictor_factory('operator-first',validate)(Model())('Test')


    def test_evaluator_retains_original_alias_and_invalid_span(self):
        from scripts import extractive_development as e
        alias = 'triggering condition'
        for raw in ({'entities':{'unrequested':[]}}, {'entities':{alias:[{'start':1,'end':4,'text':'If A','confidence':.9}]}}):
            class Model:
                def extract_entities(self,*a,**kw): return raw
            predict = predictor_factory('operator-first',e.model_spans)(Model())
            row = e.evaluate([{'id':'a','family':'one','text':'If A','labels':[['condition','If A']]}],predict)['cases'][0]
            self.assertEqual(row['raw'],raw)
            self.assertEqual(row['predicted'],[])
            self.assertIsNotNone(row['invalid_abstention'])


if __name__ == '__main__':
    unittest.main()
