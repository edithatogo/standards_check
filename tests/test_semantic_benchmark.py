import unittest
from scripts.semantic_benchmark import bidirectional, select_threshold, measures, validate_cases


class BenchmarkTest(unittest.TestCase):
    def test_bidirectional_abstains_on_one_way_and_low_confidence(self):
        self.assertTrue(bidirectional([.01,.98,.01],[.01,.97,.02],.9))
        self.assertFalse(bidirectional([.01,.98,.01],[.01,.2,.79],.9))
        self.assertFalse(bidirectional([.01,.89,.1],[.01,.97,.02],.9))
        with self.assertRaises(ValueError):
            bidirectional([0,float('nan'),1],[.01,.97,.02],.9)

    def test_threshold_uses_only_dev_and_safety(self):
        dev=[(.8,True),(.7,False),(.95,True)]
        self.assertEqual(select_threshold(dev),.8)
        self.assertEqual(select_threshold([(.99,False),(.6,True)]),1.01)
        self.assertEqual(measures([True,False,True],[True,True,False]),{'n':3,'tp':1,'fp':1,'tn':0,'fn':1,'accepted':2})

    def test_family_overlap_and_missing_direction_rejected(self):
        a={'id':'a','family':'prisma','split':'dev','source':'a','candidate':'b','forward':'entailment','reverse':'neutral'}
        b={**a,'id':'b','split':'test'}
        with self.assertRaises(ValueError):
            validate_cases([a,b])
        with self.assertRaises(ValueError):
            validate_cases([a,{**b,'family':'consort','reverse':'unknown'}])
        validate_cases([a,{**b,'family':'consort'}])
