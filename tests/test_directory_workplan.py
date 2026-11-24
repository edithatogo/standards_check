import unittest

from scripts.directory_workplan import workplan


class DirectoryWorkplanTests(unittest.TestCase):
    def receipts(self):
        revision, blob = 'a' * 40, 'b' * 40
        ids = ['a', 'b', 'c', 'd', 'e', 'f']
        catalog = {'source_revision': revision, 'published_count': len(ids),
                   'guidelines': [{'id': i, 'source_blob_sha': blob} for i in ids]}
        survey = {'source_revision': revision, 'summary': {'published_count': len(ids), 'canonical_packs_promoted': 0},
                  'records': [{**r, 'status': 'oa_xml_candidate', 'resolved_doi': '10.1234/' + r['id'],
                               'pmcid': 'PMC' + str(n)} for n, r in enumerate(catalog['guidelines'], 1)],
                  'bulk_articles': [{'pmcid': 'PMC1', 'doi': '10.1234/a', 'status': 'deferred_acquisition_budget'},
                                    {'pmcid': 'PMC2', 'doi': '10.1234/b', 'status': 'held'},
                                    {'pmcid': 'PMC3', 'doi': '10.1234/c', 'status': 'source_inventory_observed_not_reconciled',
                                     'source_sha256': 'c' * 64, 'source_blobs': [['c', blob]]},
                                    {'pmcid': 'PMC4', 'doi': '10.1234/d', 'status': 'expected_numbered_rows_observed',
                                     'source_sha256': 'd' * 64, 'matched_rows': 5}]}
        survey['records'][4]['provider_disagreements'] = ['identity']
        survey['records'][5]['status'] = 'lookup_incomplete'
        links = {'source_revision': revision, 'published_count': len(ids),
                 'guidelines': [{**r, 'candidates': []} for r in catalog['guidelines']]}
        return catalog, survey, links

    def test_all_entries_routed_without_admission(self):
        report = workplan(*self.receipts())
        self.assertEqual(report['published_count'], 6)
        self.assertEqual(sum(report['next_action_counts'].values()), 6)
        self.assertEqual([r['next_action'] for r in report['records']], [
            'resume_acquisition_budget', 'retry_acquisition_or_alternative', 'extract_anchored_candidates',
            'qualify_structure_rights_and_interpretation', 'hold_identity_conflict', 'resume_provider_lookup'])
        self.assertEqual(report['canonical_packs_promoted'], 0)
        self.assertTrue(all(r['admission'] == 'not_assessed' for r in report['records']))

    def test_fail_closed_on_drift_incomplete_or_duplicate(self):
        for mutate in (lambda c, s, l: s['records'].pop(),
                       lambda c, s, l: l['guidelines'].append(l['guidelines'][0]),
                       lambda c, s, l: s.update(source_revision='c' * 40),
                       lambda c, s, l: s['records'][0].update(source_blob_sha='c' * 40),
                       lambda c, s, l: s['summary'].update(canonical_packs_promoted=1),
                       lambda c, s, l: s['bulk_articles'][2].update(source_sha256='invalid')):
            c, s, l = self.receipts()
            mutate(c, s, l)
            with self.assertRaises(ValueError):
                workplan(c, s, l)

    def test_unbound_source_and_metadata_routes(self):
        c, s, l = self.receipts()
        s['bulk_articles'][2]['source_blobs'] = [['c', 'd' * 40]]
        s['records'][0]['status'] = 'metadata_only'
        l['guidelines'][0]['candidates'] = [{'url': 'https://example.org'}]
        s['records'][1]['status'] = 'metadata_only'
        s['records'][3]['status'] = 'missing_identifier'
        s['records'][4].pop('provider_disagreements')
        report = workplan(c, s, l)
        self.assertEqual([r['next_action'] for r in report['records']], [
            'qualify_source_link', 'locate_authoritative_source', 'hold_source_binding',
            'resolve_identity', 'acquire_exact_source', 'resume_provider_lookup'])
