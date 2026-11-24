import unittest
from scripts.witness_adjudication import witness_mask, witness_label, witness_vote, control_input

class WitnessTests(unittest.TestCase):
    def test_all_five_compliance_relationships(self):
        self.assertEqual(witness_label([3,4], [3,4]), 'equivalent')
        self.assertEqual(witness_label([3,4], [4]), 'narrower')
        self.assertEqual(witness_label([4], [3,4]), 'broader')
        self.assertEqual(witness_label([3,4], [1,2]), 'contradictory')
        self.assertEqual(witness_label([3,4], [2,4]), 'indeterminate')

    def test_invalid_witnesses_abstain(self):
        for invalid in ([], [True], [0], [5], [1,1], ['1'], None):
            self.assertIsNone(witness_mask(invalid))
            self.assertEqual(witness_label(invalid, [4]), 'abstain')
        self.assertEqual(witness_mask([4,1]), 9)

    def test_control_detection_requires_both_texts(self):
        prefix='In this controlled example the two reporting checks are independent.'
        self.assertTrue(control_input({'source':prefix+'\nX','candidate':prefix+'\nY'}))
        self.assertFalse(control_input({'source':prefix+'\nX','candidate':'Y'}))

    def test_valid_span_and_derived_relation(self):
        p={'id':'x','source':'First.\nSecond.','candidate':'Third.'}
        v=witness_vote(p,{'a_compliant':[3,4],'b_compliant':[4],'a':[2],'b':[1]})
        self.assertEqual(v['label'],'narrower')
        self.assertEqual(v['a_spans'],[[7,14]])
        self.assertEqual(v['a_compliant'],[3,4])
        self.assertEqual(witness_vote(p,{'a_compliant':[3,4],'b_compliant':[4],'a':[3],'b':[1]})['label'],'abstain')
        self.assertEqual(witness_vote(p,{'a_compliant':[3,4],'b_compliant':[4],'a':[2],'b':[1],'label':'equivalent'})['label'],'abstain')
