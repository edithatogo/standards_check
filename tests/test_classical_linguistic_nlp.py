"""Synthetic discrepancy tests; no real-source or model qualification claim."""
import json
import unittest

from scripts.classical_linguistic_nlp import compare, describe
from scripts.lexical_text import normalise


class RuleTests(unittest.TestCase):
    def test_unicode_and_identical_text(self):
        self.assertEqual(normalise('ＣＡＦÉ\u00a0 ２!'), 'café 2')
        result = compare('Report all outcomes.', 'Report all outcomes.')
        self.assertEqual(result['lexical_similarity'], 1.0)
        self.assertEqual(result['changed_fields'], [])
        self.assertEqual(result['canonical_packs_promoted'], 0)

    def test_single_change_negatives(self):
        for left, right, field in [
            ('Must report outcomes.', 'Should report outcomes.', 'modality'),
            ('Must not report identifiers.', 'Must report identifiers.', 'negation'),
            ('Report 2 outcomes.', 'Report 3 outcomes.', 'quantification'),
            ('Report 5% of outcomes.', 'Report 5 outcomes.', 'quantification'),
            ('Report -2 outcomes.', 'Report 2 outcomes.', 'quantification'),
            ('Report all outcomes.', 'Report some outcomes.', 'quantification'),
            ('Report A and B.', 'Report A or B.', 'logic'),
            ('Report A unless exempt.', 'Report A.', 'conditionality'),
            ('Report before discharge.', 'Report after discharge.', 'conditionality'),
            ('If eligible, report A.', 'If ineligible, report A.', 'conditionality'),
            ('Report A except B.', 'Report A.', 'logic'),
        ]:
            with self.subTest(field=field, left=left):
                result = compare(left, right)
                self.assertIn(field, result['changed_fields'])
                self.assertEqual(result['status'], 'diagnostic_only')

    def test_offsets_and_no_prose_leak(self):
        text = 'Clinicians must not disclose private identifiers before review.'
        result = describe(text)
        self.assertEqual(result['syntax_status'], 'not_run')
        for field in ('modality', 'negation', 'conditionality'):
            for cue in result[field]:
                self.assertTrue(text[cue['start']:cue['end']])
        self.assertNotIn('private identifiers', json.dumps(result))
        self.assertEqual(describe('Report not only A but also B.')['negation'], [])
        self.assertTrue(describe('If eligible, staff must report.')['conditional_obligation_candidate'])
        self.assertEqual(describe('Staff may report.')['modality'][0]['kind'], 'permission')
        self.assertEqual(compare('', 'Report.')['status'], 'held_input')
        self.assertEqual(compare('x' * 8193, 'Report.')['status'], 'held_input')


class ReferenceTests(unittest.TestCase):
    def test_spacy_dependency_roles_and_scope(self):
        try:
            import spacy
            from spacy.tokens import Doc
        except ImportError:
            self.skipTest('optional spaCy reference not installed')
        vocab = spacy.blank('en').vocab
        words = ['Staff', 'must', 'not', 'record', 'evidence', '.']
        doc = Doc(vocab, words=words, spaces=[True, True, True, True, False, False],
                  heads=[3, 3, 3, 3, 3, 3], deps=['nsubj', 'aux', 'neg', 'ROOT', 'dobj', 'punct'],
                  pos=['NOUN', 'AUX', 'PART', 'VERB', 'NOUN', 'PUNCT'],
                  lemmas=['staff', 'must', 'not', 'record', 'evidence', '.'])
        result = describe(doc.text, lambda _: doc)
        self.assertEqual(result['syntax_status'], 'parsed_reference')
        self.assertEqual(len(result['tokens']), 6)
        roles = result['semantic_roles']
        self.assertEqual({r['kind'] for r in roles}, {'action', 'subject', 'object', 'evidence_candidate'})
        self.assertEqual(result['dependency_negation'][0]['head'], 3)
        self.assertEqual(result['tokens'][3]['pos'], 'VERB')
        self.assertNotIn('Staff must', json.dumps(result))
        blank = spacy.blank('en')
        with self.assertRaisesRegex(ValueError, 'annotations'):
            describe(doc.text, blank)


if __name__ == '__main__':
    unittest.main()
