import unittest
from scripts.five_class_benchmark import relation, forms, evidence_spans, validate_index_vote, qualification, material_deficit

class FiveClassTests(unittest.TestCase):
    def test_truth_table_all_classes(self):
        self.assertEqual([relation(a,b) for a,b in forms()], ['equivalent','narrower','broader','contradictory','indeterminate'])

    def test_span_selection_abstains_on_invalid(self):
        p={'id':'x','source':'First.\nSecond.','candidate':'Third.'}
        self.assertEqual(evidence_spans(p['source']), [(0,6),(7,14)])
        a=validate_index_vote(p,{'label':'narrower','a':[2],'b':[1]})
        self.assertEqual(a['a_spans'], [[7,14]])
        self.assertEqual(a['label'],'narrower')
        self.assertEqual(validate_index_vote(p,{'label':'narrower','a':[3],'b':[1]})['label'],'abstain')
        self.assertEqual(validate_index_vote(p,{'label':'narrower','a':[True],'b':[1]})['label'],'abstain')

    def test_gate_needs_classes_families_and_correct_controls(self):
        labels=['equivalent','narrower','broader','contradictory','indeterminate']
        rows=[{'split':split,'family':family,'reference':l,'agent_a':l,'agent_b':l,'label':l} for split,family in [('dev','a'),('test','b'),('test','c')] for l in labels]
        self.assertTrue(qualification(rows)['qualified'])
        self.assertFalse(qualification([r for r in rows if r['reference']!='broader'])['qualified'])
        self.assertFalse(qualification([{**r,'label':'equivalent','agent_a':'equivalent','agent_b':'equivalent'} for r in rows])['qualified'])

    def test_escalation_only_on_material_heldout_errors(self):
        rows=[{'split':'test','family':str(i%2),'reference':'broader','predicted':'broader'} for i in range(10)]
        self.assertFalse(material_deficit(rows)['eligible'])
        for r in rows[:2]: r['predicted']='contradictory'
        self.assertTrue(material_deficit(rows)['eligible'])
        self.assertFalse(material_deficit(rows[:3])['eligible'])
