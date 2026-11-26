import json
import hashlib
import pytest
from searchright_bridge import crosswalk, project_records, read_pinned


def test_crosswalk_conserves_rows_and_never_authorizes_execution():
    inputs = {
        'policies': {'providers': [{'provider_id': 'crossref', 'access_class': 'open'}]},
        'methods': [{'source_id': 'opencitations', 'method': 'forward_citation', 'access_mode': 'fixture_adapter'}],
        'advisory': {'sources': [{'source_id': 'medline', 'platforms': [{'platform_id': 'pubmed', 'access': 'free'}, {'platform_id': 'ovid', 'access': 'licensed'}]}]},
        'directories': {'directories': [{'directory_id': 'refhunter', 'directory_type': 'database_capability_directory'}]},
    }
    result = crosswalk(inputs)
    assert len(result) == 4
    assert all(not x['execution_authorized'] for x in result)
    assert result[2]['platforms'] == inputs['advisory']['sources'][0]['platforms']
    inputs['methods'].append(inputs['methods'][0])
    with pytest.raises(ValueError, match='duplicate'): crosswalk(inputs)


def test_only_exact_work_observations_project_and_no_edition_merge():
    task = {'task_id': 'task', 'catalogue_ids': ['a', 'b'], 'value': '10.1000/example', 'kind': 'doi', 'observed_at': '2026-11-26T00:00:00Z', 'observations': [
        {'provider':'crossref','response_sha256':'a'*64,'result':{'status':'exact_doi_metadata','doi':'10.1000/example','title':'Actual publication','cited_by_count':0,'orcid_observations':['0000-0002-1825-0097']}},
        {'provider':'openalex','response_sha256':'b'*64,'result':{'status':'identifier_conflict','doi':'10.1000/other','title':'Wrong'}},
    ]}
    rows = project_records({'observations':[task]})
    assert len(rows) == 1
    assert rows[0]['identifiers']['doi'] == '10.1000/example'
    assert rows[0]['provider_metadata']['catalogue_ids'] == ['a', 'b']
    assert rows[0]['provider_metadata']['edition_qualified'] is False
    assert rows[0]['provider_metadata']['observation']['cited_by_count'] == 0
    assert rows[0]['abstract_text'] is None
    assert project_records({'observations':[]}) == []


def test_pinned_bytes_fail_closed(tmp_path):
    p = tmp_path/'a.json'; p.write_bytes(b'{"x":1}\n')
    pin = hashlib.sha1(b'blob '+str(p.stat().st_size).encode()+b'\0'+p.read_bytes()).hexdigest()
    assert read_pinned(p,pin) == {'x':1}
    p.write_text('{}')
    with pytest.raises(ValueError,match='blob'):read_pinned(p,pin)
