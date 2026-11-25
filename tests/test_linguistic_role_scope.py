"""Regression cases for observed development-set role/scope failures."""
import unittest

from scripts.classical_linguistic_nlp import compare


class ScopeTests(unittest.TestCase):
    def test_explicit_coordination_grouping(self):
        result = compare('List (cost and harm) or benefit.', 'List cost and (harm or benefit).')
        self.assertIn('logic', result['changed_fields'])
        self.assertEqual(result['canonical_packs_promoted'], 0)
        self.assertNotIn('logic', compare('List cost (USD) and harm.', 'List cost and harm.')['changed_fields'])


class RoleTests(unittest.TestCase):
    def test_role_identity_invariant_to_voice_and_modality_but_not_actor(self):
        try:
            import spacy
            from spacy.tokens import Doc
        except ImportError:
            self.skipTest('optional spaCy reference not installed')
        vocab = spacy.blank('en').vocab

        def active(modal='must', patient='result'):
            return Doc(vocab, words=['The', 'nurse', modal, 'record', 'the', patient, '.'],
                       spaces=[True, True, True, True, True, False, False],
                       heads=[1, 3, 3, 3, 5, 3, 3],
                       deps=['det', 'nsubj', 'aux', 'ROOT', 'det', 'dobj', 'punct'],
                       pos=['DET', 'NOUN', 'AUX', 'VERB', 'DET', 'NOUN', 'PUNCT'],
                       lemmas=['the', 'nurse', modal, 'record', 'the', patient, '.'])

        def passive(actor='nurse'):
            return Doc(vocab, words=['The', 'result', 'must', 'be', 'recorded', 'by', 'the', actor, '.'],
                       spaces=[True, True, True, True, True, True, True, False, False],
                       heads=[1, 4, 4, 4, 4, 4, 7, 5, 4],
                       deps=['det', 'nsubjpass', 'aux', 'auxpass', 'ROOT', 'agent', 'det', 'pobj', 'punct'],
                       pos=['DET', 'NOUN', 'AUX', 'AUX', 'VERB', 'ADP', 'DET', 'NOUN', 'PUNCT'],
                       lemmas=['the', 'result', 'must', 'be', 'record', 'by', 'the', actor, '.'])

        def pair(a, b):
            docs = {doc.text: doc for doc in (a, b)}
            return compare(a.text, b.text, docs.__getitem__)['changed_fields']

        self.assertNotIn('semantic_roles', pair(active(), passive()))
        self.assertNotIn('semantic_roles', pair(active(), active(modal='should')))
        self.assertIn('semantic_roles', pair(passive(), passive(actor='doctor')))
        self.assertIn('semantic_roles', pair(active(), active(patient='consent')))
