import unittest
from scripts.blind_adjudication import blinded_cases, validate_vote, consensus, classify_nli, escalation


class BlindAdjudicationTests(unittest.TestCase):
    def test_no_prediction_or_stratum_leaks_into_prompt_input(self):
        row={'id':'abc','family':'cheers','source':'Report harms.','candidate':'Report harms and benefits.','intended':'narrower','prediction':'equivalent'}
        self.assertEqual(blinded_cases([row]),[{'id':'abc','source':'Report harms.','candidate':'Report harms and benefits.'}])

    def test_invalid_quotes_and_disagreement_abstain(self):
        pair={'id':'x','source':'Report harms.','candidate':'Do not report harms.'}
        a=validate_vote(pair,{'label':'contradictory','a_quote':'Report harms','b_quote':'Do not report harms'})
        b=validate_vote(pair,{'label':'equivalent','a_quote':'fake','b_quote':'harms'})
        self.assertEqual(a['label'],'contradictory')
        self.assertEqual(b['label'],'abstain')
        self.assertEqual(consensus(a,b),'abstain')
        self.assertEqual(consensus(a,a),'contradictory')
        self.assertNotIn('Report harms',str(a))

    def test_directional_classes_and_confidence(self):
        e=(.01,.98,.01);n=(.05,.05,.90);c=(.90,.05,.05)
        self.assertEqual([classify_nli(*p) for p in [(e,e),(n,e),(e,n),(c,c),(n,n),(e,c)]],['equivalent','narrower','broader','contradictory','indeterminate','abstain'])
        self.assertEqual(classify_nli((.01,.89,.1),e),'abstain')

    def test_escalation_requires_enough_agreement_and_repeated_errors(self):
        good=[{'split':'test','family':str(i%2),'label':'broader','predicted':'broader'} for i in range(10)]
        self.assertFalse(escalation(good)['eligible'])
        bad=[{**r,'predicted':'equivalent'} if i<2 else r for i,r in enumerate(good)]
        self.assertTrue(escalation(bad)['eligible'])
        self.assertFalse(escalation(bad[:3])['eligible'])
        self.assertFalse(escalation(bad+[{'split':'test','family':'a','label':'abstain','predicted':'equivalent'}]*20)['eligible'])
