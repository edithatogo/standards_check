import unittest
from scripts.source_reconciliation import linguistic_compare, layout_rows, item_findings, project, validate_tables


class SourceReconciliationTests(unittest.TestCase):
    def test_material_linguistic_changes(self):
        pairs = [
            ('Report harms.', 'Do not report harms.', 'polarity'),
            ('Must report harms.', 'May report harms.', 'modality'),
            ('Report harms and benefits.', 'Report harms or benefits.', 'logic'),
            ('Report at least 3 events.', 'Report at most 2 events.', 'quantity'),
            ('If eligible, report outcomes.', 'Report outcomes.', 'condition'),
            ('Report before treatment.', 'Report after treatment.', 'temporal'),
            ('Report harms.', 'Report benefits.', 'lexical'),
            ('Do not report harms; report benefits.', 'Report harms; do not report benefits.', 'polarity'),
        ]
        for source, candidate, code in pairs:
            with self.subTest(code=code):
                result = linguistic_compare(source, candidate)
                self.assertIn(code, result['findings'])
                self.assertFalse(result['exact'])
                self.assertNotIn(source, str(result))
        self.assertTrue(linguistic_compare('Report harms.', 'Report harms.')['exact'])

    def test_layout_uses_header_and_whole_requirement(self):
        rows, issues = layout_rows('Topic   Sub-item number   Sub-item                 Score\n'
                                   'Study   1.1               Report all outcomes.     2.1\n'
                                   '                          Include missing data.\n'
                                   '        1.2               Report harms.\n')
        self.assertEqual([r['item_id'] for r in rows], ['1.1', '1.2'])
        self.assertEqual(rows[0]['requirement_sha256'], linguistic_compare('Report all outcomes. Include missing data.', '')['source_sha256'])
        self.assertEqual(issues, [])
        self.assertEqual(rows[0]['requirement_anchor'], 'page/1/lines/2-3')

    def test_layout_holds_unbound_and_duplicate_rows(self):
        rows, issues = layout_rows('Sub-item number   Sub-item\n1.1               Report harms.\n'
                                   '2.1\n1.1               Different.\n\f1.2               Unbound.\n')
        self.assertIn('missing_header', issues)
        self.assertIn('duplicate_id', issues)
        self.assertIsNone(rows[1]['requirement_sha256'])
        self.assertEqual(layout_rows('1.1  Unbound')[0], [])

    def test_no_admission_and_ambiguous_alignment(self):
        source = {'item_id': '1', 'text': 'Report harms.'}
        legacy = [{'declared_item_id': '1', 'position': 1, 'text': 'Report harms.'},
                  {'declared_item_id': '1', 'position': 2, 'text': 'Report harms.'}]
        outcome = item_findings(source, legacy)
        self.assertEqual(outcome['status'], 'held_ambiguous_alignment')
        self.assertIsNone(outcome['legacy_position'])
        outcome = item_findings(source, legacy[:1])
        self.assertEqual(outcome['status'], 'exact_text_candidate')
        self.assertEqual(item_findings(source, [])['status'], 'held_unaligned')

    def test_projection_preserves_rows_without_text_or_promotion(self):
        catalogue = {'guidelines': [{'id': 'equator:a', 'source_blob_sha': 'a'*40}]}
        pack = {'pack_id': 'org/a/1', 'version': '1', 'verification': {'status': 'source_reconciled'},
                'rights': {'status': 'cleared'}, 'authority': {'source_sha256': 'b'*64},
                'requirements': [{'id': 'A:1', 'source_anchor': 'table:1', 'verbatim_text': 'Secret example.',
                                  'rights': {'inherit_from_pack': True}}]}
        article = {'editions': [{'edition': 'Example', 'status': 'table_items_extracted_legacy_compared',
                   'source': {'source_sha256': 'c'*64, 'rows': [{'item_id': '1', 'source_anchor': 't:row:1:item:1', 'text': 'Report harms.'}]}}]}
        tables = project(catalogue, [pack], article, {'sources': []}, {'Example': [{'declared_item_id': '1', 'position': 1, 'text': 'Report harms.'}]})
        self.assertEqual(len(tables['requirements']), 2)
        self.assertEqual(len(tables['guidelines']), 3)
        self.assertNotIn('Secret example.', str(tables))
        self.assertNotIn('Report harms.', str(tables))
        self.assertEqual(tables['admission_decisions'][0]['disposition'], 'held_independent_review')
        self.assertTrue(tables['admission_decisions'][0]['independent_sample'])
        validate_tables(tables)
        tables['requirements'].append(tables['requirements'][0])
        with self.assertRaises(ValueError):
            validate_tables(tables)

    def test_missing_source_stays_held(self):
        tables = project({'guidelines': []}, [], {'editions': [{'edition': 'Missing', 'status': 'held'}]}, {'sources': []}, {})
        self.assertEqual(tables['sources'][0]['status'], 'held')
        self.assertEqual(tables['admission_decisions'][0]['disposition'], 'held_source')
        self.assertEqual(tables['requirements'], [])
