import copy

import pytest

from scripts.equator_pipeline_coverage import coverage


def inputs():
    r = 'r'
    source = {'id': 'equator:a', 'source_blob_sha': 'blob'}
    cat = {'source_revision': r, 'published_count': 1, 'guidelines': [{**source,
           'metadata_status': 'extracted_unverified', 'study_types': ['Trial']}]}
    links = {'source_revision': r, 'published_count': 1, 'guidelines': [{**source,
              'candidates': [{'url': 'https://example.org'}]}]}
    survey = {'source_revision': r, 'summary': {'published_count': 1},
              'records': [{**source, 'status': 'oa_xml_candidate', 'rights': 'unassessed', 'pmcid': 'PMC1'}],
              'oa_source_worklist': [{'pmcid': 'PMC1', 'source_ids': ['equator:a'],
                                     'status': 'candidate_pending_acquisition'}],
              'bulk_articles': [{'pmcid': 'PMC1', 'source_blobs': [['equator:a', 'blob']],
                                 'status': 'deferred_acquisition_budget'}], 'priority_articles': []}
    legacy = {'equator_revision': r, 'equator_published_count': 1, 'legacy_items': [
        {'legacy_id': 'a-old', 'equator_candidate': source, 'source_assets': [{'path': 'old.pdf'}],
         'legacy_views': [{'path': 'old.md'}]}]}
    return cat, links, survey, legacy


def test_census_keeps_candidates_separate_from_execution_and_rights():
    report = coverage(*inputs())
    assert report['summary']['directory_entries'] == 1
    assert report['summary']['with_source_link_candidates'] == 1
    assert report['summary']['with_legacy_original_candidates'] == 1
    assert report['summary']['end_to_end_qualified_from_these_receipts'] == 0
    row = report['rows'][0]
    assert row['source_observation'] == 'deferred_acquisition_budget'
    assert row['rights_observation'] == 'unassessed'
    assert row['pipeline_evaluation'] == 'not_evidenced_in_source_receipts'
    assert report['study_type_strata']['Trial']['entries'] == 1


def test_reject_stale_and_nonconserved_census_inputs():
    for i, key in ((0, 'source_revision'), (1, 'source_revision'), (2, 'source_revision'), (3, 'equator_revision')):
        args = list(copy.deepcopy(inputs()))
        args[i][key] = 'other' if i else 'different'
        with pytest.raises(ValueError, match='revision'):
            coverage(*args)
    args = list(inputs())
    args[2]['records'][0]['source_blob_sha'] = 'wrong'
    with pytest.raises(ValueError, match='blob'):
        coverage(*args)
    args = list(inputs())
    args[1]['guidelines'] = []
    with pytest.raises(ValueError, match='inventory'):
        coverage(*args)
    args = list(inputs())
    args[2]['records'].append(args[2]['records'][0])
    with pytest.raises(ValueError, match='duplicate'):
        coverage(*args)


def test_cli_archive_and_directory_same_member_hashes(tmp_path, monkeypatch):
    import json
    import zipfile
    from scripts import equator_pipeline_coverage as module

    files = dict(zip(module.MEMBERS, inputs(), strict=True))
    archive, out = tmp_path / 'a.zip', tmp_path / 'report.json'
    with zipfile.ZipFile(archive, 'w') as bundle:
        for name, data in files.items():
            raw = json.dumps(data)
            bundle.writestr(name, raw)
            (tmp_path / name).write_text(raw)
    monkeypatch.setattr('sys.argv', ['coverage', '--artifact', str(archive), '--output', str(out)])
    module.main()
    zipped = json.loads(out.read_text())
    assert len(zipped['archive_sha256']) == 64
    monkeypatch.setattr('sys.argv', ['coverage', '--directory', str(tmp_path), '--output', str(out)])
    module.main()
    directory = json.loads(out.read_text())
    assert directory['archive_sha256'] is None
    assert zipped['member_sha256'] == directory['member_sha256']
    assert zipped['rows'] == directory['rows']


def test_missing_and_multiple_source_observations_and_invalid_links():
    args = list(inputs())
    args[2]['bulk_articles'] = []
    assert coverage(*args)['rows'][0]['source_observation'] == 'not_evidenced_in_bulk_receipt'
    args = list(inputs())
    args[2]['bulk_articles'].append({**args[2]['bulk_articles'][0], 'status': 'held'})
    assert coverage(*args)['rows'][0]['source_observation'] == 'multiple_bulk_observations'
    args[2]['oa_source_worklist'][0]['source_ids'] = ['equator:outside']
    with pytest.raises(ValueError, match='worklist'):
        coverage(*args)
