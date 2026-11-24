import unittest
from scripts.witness_adjudication import condition_vote


class ConditionTests(unittest.TestCase):
    def test_all_relationships_derived_from_independent_conditions(self):
        p={'id':'x','source':'First.\nCondition.','candidate':'Second.\nCondition.'}
        for a,b,label in [('P','P','equivalent'),('P','P_AND_Q','narrower'),('P_AND_Q','P','broader'),('P','NOT_P','contradictory'),('P','Q','indeterminate')]:
            with self.subTest(a=a,b=b):
                result=condition_vote(p,{'a_condition':a,'b_condition':b,'a':[2],'b':[2]})
                self.assertEqual(result['label'],label)
                self.assertEqual(result['a_spans'],[[7,17]])

    def test_invalid_condition_or_evidence_never_forces_label(self):
        p={'id':'x','source':'First.\nCondition.','candidate':'Second.\nCondition.'}
        good={'a_condition':'P','b_condition':'P_AND_Q','a':[2],'b':[2]}
        self.assertEqual(condition_vote(p,good)['label'],'narrower')
        for bad in ({'a_condition':'abstain'},{'a_condition':None},{'a_condition':[]},{'b':[1]},{'label':'equivalent'}):
            with self.subTest(bad=bad):
                self.assertEqual(condition_vote(p,{**good,**bad})['label'],'abstain')
