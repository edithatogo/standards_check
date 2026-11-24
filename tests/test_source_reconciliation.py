import unittest
import importlib.util
import tempfile
from pathlib import Path
from scripts.source_reconciliation import linguistic_compare, layout_rows, item_findings, project, validate_tables, write_parquet


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
        wrong_id = [{'declared_item_id': '2', 'position': 1, 'text': 'Report harms.'}]
        self.assertEqual(item_findings(source, wrong_id)['status'], 'held_ambiguous_alignment')

    def test_projection_preserves_rows_without_text_or_promotion(self):
        catalogue = {'guidelines': [{'id': 'equator:a', 'source_blob_sha': 'a'*40}]}
        pack = {'pack_id': 'org/a/1', 'version': '1', 'verification': {'status': 'source_reconciled'},
                'rights': {'status': 'cleared', 'spdx': 'CC-BY-4.0', 'attribution': 'Synthetic author'},
                'authority': {'source_sha256': 'b'*64},
                'requirements': [{'id': 'A:1', 'source_anchor': 'table:1', 'verbatim_text': 'Secret example.',
                                  'rights': {'inherit_from_pack': True}}]}
        article = {'editions': [{'edition': 'Example', 'status': 'table_items_extracted_legacy_compared',
                   'source': {'source_sha256': 'c'*64, 'rows': [{'item_id': '1', 'source_anchor': 't:row:1:item:1', 'text': 'Report harms.'}]}}]}
        tables = project(catalogue, [pack], article, {'sources': []}, {'Example': [{'declared_item_id': '1', 'position': 1, 'text': 'Report harms.'}]})
        self.assertEqual(len(tables['requirements']), 2)
        self.assertEqual(len(tables['guidelines']), 3)
        self.assertEqual(tables['canonical_requirements'][0]['verbatim_text'], 'Secret example.')
        self.assertEqual(tables['canonical_requirements'][0]['spdx'], 'CC-BY-4.0')
        self.assertEqual(tables['canonical_requirements'][0]['attribution'], 'Synthetic author')
        self.assertNotIn('Secret example.', str(tables['requirements']))
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

    def test_candidate_cross_format_missing_duplicate_and_discrepant_rows(self):
        def row(item, digest):
            return {'item_id': item, 'requirement_sha256': digest, 'requirement_anchor': 'table/1'}
        ecoevo = {'expected_item_ids': ['1.1', '1.2', '1.3'],
                  'sources': [{'path': 'a.pdf', 'rows': [row('1.1', 'a'*64), row('1.2', 'a'*64), row('1.2', 'a'*64)]},
                              {'path': 'b.csv', 'rows': [row('1.1', 'b'*64), row('1.2', 'a'*64)]}]}
        tables = project({'guidelines': []}, [], {'editions': []}, ecoevo, {})
        statuses = {r['item_id']: r['status'] for r in tables['format_comparisons']}
        self.assertEqual(statuses, {'1.1': 'held_text_discrepancy', '1.2': 'held_missing_or_ambiguous', '1.3': 'held_missing_or_ambiguous'})

    def test_uncleared_canonical_prose_is_not_exported(self):
        pack = {'pack_id': 'org/a/1', 'version': '1', 'verification': {'status': 'imported_unverified'},
                'rights': {'status': 'cleared'}, 'authority': {},
                'requirements': [{'id': 'A:1', 'source_anchor': 'a', 'verbatim_text': 'Restricted.',
                                  'normalized_requirement': 'Restricted.', 'rights': {'status': 'restricted'}}]}
        tables = project({'guidelines': []}, [pack], {'editions': []}, {'sources': []}, {})
        self.assertNotIn('Restricted.', str(tables))
        self.assertIsNone(tables['canonical_requirements'][0]['verbatim_text'])

    @unittest.skipUnless(importlib.util.find_spec('polars'), 'Parquet dependency not installed')
    def test_parquet_roundtrip_preserves_explicit_schema_and_empty_tables(self):
        import polars as pl
        tables = project({'guidelines': [{'id': 'equator:a', 'source_blob_sha': 'a'*40}]}, [],
                         {'editions': []}, {'sources': []}, {})
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            manifest = write_parquet(tables, output)
            self.assertEqual(set(manifest['tables']), set(tables))
            self.assertEqual(pl.read_parquet(output / 'guidelines.parquet').height, 1)
            self.assertEqual(pl.read_parquet(output / 'requirements.parquet').height, 0)
            self.assertEqual(pl.read_parquet(output / 'requirements.parquet').schema['ordinal'], pl.Int64)

    @unittest.skipUnless(importlib.util.find_spec('polars'), 'Parquet dependency not installed')
    def test_cli_replays_pinned_retained_corpus_and_existing_survey(self):
        import json
        import sys
        from unittest.mock import patch
        import polars as pl
        from scripts.source_reconciliation import main
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            ecoevo = base / 'ecoevo.json'
            ecoevo.write_text(json.dumps({'sources': []}), encoding='utf-8')
            survey = base / 'survey.json'
            survey.write_text(json.dumps({'records': [{'id': 'equator:test', 'status': 'lookup_incomplete'}]}), encoding='utf-8')
            output = base / 'out'
            with patch.object(sys, 'argv', ['source_reconciliation', '--root', str(root),
                                          '--ecoevo', str(ecoevo), '--survey', str(survey),
                                          '--output', str(output), '--revision', 'synthetic-test-revision']):
                main()
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['canonical_packs_promoted'], 0)
            self.assertTrue((output / 'survey-retrospective.json').is_file())
            canonical = pl.read_parquet(output / 'canonical_requirements.parquet')
            self.assertGreaterEqual(canonical.height, 42)
            self.assertEqual(canonical.filter(pl.col('rights') != 'cleared')['verbatim_text'].drop_nulls().len(), 0)
            self.assertGreater(pl.read_parquet(output / 'comparisons.parquet').height, 0)

    def test_validator_rejects_orphans_and_wrong_types(self):
        tables = project({'guidelines': [{'id': 'equator:a', 'source_blob_sha': 'a'*40}]}, [],
                         {'editions': []}, {'sources': []}, {})
        tables['sources'][0]['guideline_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'relationship'):
            validate_tables(tables)
        tables['sources'][0]['guideline_id'] = 'equator:a'
        tables['sources'][0]['format'] = 1
        with self.assertRaisesRegex(ValueError, 'value type'):
            validate_tables(tables)
