import pytest
from bibliographic_recovery import link_id, plan, metadata, title_candidates, select_tasks, orcid


def test_identifiers_only_from_explicit_known_routes():
    assert link_id('https://doi.org/10.1002/ABC.1') == ('doi', '10.1002/abc.1')
    assert link_id('https://www.ncbi.nlm.nih.gov/pubmed/12345') == ('pmid', '12345')
    assert link_id('https://pmc.ncbi.nlm.nih.gov/articles/PMC123/') == ('pmcid', 'PMC123')
    assert link_id('https://link.springer.com/article/10.1007/s1234') == ('doi', '10.1007/s1234')
    assert link_id('https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1234567') == ('doi', '10.1371/journal.pmed.1234567')
    for url in ('https://evil.test/10.1002/abc.1', 'https://doi.org@evil.test/10.1002/abc.1', 'https://pubmed.ncbi.nlm.nih.gov/123/extra', 'https://doi.org:8080/10.1002/abc.1', 'https://doi.org/invalid'):
        assert link_id(url) is None


def fixture():
    c = {'source_revision': 'r', 'guidelines': [{'id': i, 'source_blob_sha': i, 'title': 'Title '+i} for i in 'abcd']}
    l = {'source_revision': 'r', 'guidelines': [{'id': i, 'source_blob_sha': i, 'candidates': []} for i in 'abcd']}
    l['guidelines'][0]['candidates'] = [{'url': 'https://doi.org/10.1002/abc', 'type': 'doi_landing_candidate'}, {'url': 'https://pubmed.ncbi.nlm.nih.gov/123/', 'type': 'landing_page_candidate'}]
    l['guidelines'][1]['candidates'] = [{'url': 'https://doi.org/10.1002/abc', 'type': 'doi_landing_candidate'}]
    s = {'source_revision': 'r', 'records': [{'id': i, 'source_blob_sha': i, 'status': 'missing_identifier'} for i in 'abcd'], 'provider_evidence': {'records': {}}}
    s['records'][2].update(doi='10.1002/abc', pmid='111', status='metadata_only')
    return c, l, s


def test_plan_keeps_all_identities_and_never_merges_link_candidates():
    c,l,s = fixture(); result=plan(c,l,s)
    assert len(result['rows']) == 4
    assert result['rows'][0]['route'] == 'link_identifier_candidate'
    assert result['rows'][3]['route'] == 'title_discovery_candidate'
    assert result['shared_link_candidates'] == {'doi:10.1002/abc': ['a','b']}
    assert result['rows'][0]['publication_identity'] == []
    tasks=select_tasks(result, 3)
    assert len(tasks) <= 3 and len({(t['kind'],t['value']) for t in tasks}) == len(tasks)
    s['records'][1]['source_blob_sha']='changed'
    with pytest.raises(ValueError, match='blob'): plan(c,l,s)


def test_conflicts_and_missing_metrics_fail_closed():
    assert metadata({'DOI':'10.1002/other'}, 'crossref', '10.1002/abc')['status']=='identifier_conflict'
    r=metadata({'DOI':'10.1002/abc','is-referenced-by-count':0,'author':[{'ORCID':'https://orcid.org/0000-0002-1825-0097'},{'ORCID':'bad'}]},'crossref','10.1002/abc')
    assert r['cited_by_count']==0 and r['reference_count'] is None
    assert r['orcid_observations']==['0000-0002-1825-0097']
    assert orcid('0000-0002-1825-0098') is None
    assert metadata({'doi':'https://doi.org/10.1002/abc','ids':{'doi':'https://doi.org/10.1002/abc','pmid':'https://pubmed.ncbi.nlm.nih.gov/123/'},'id':'https://openalex.org/W1'},'openalex','10.1002/abc')['status']=='exact_doi_metadata'


def test_title_is_discovery_only_and_retains_distinct_dois():
    items=[{'DOI':'10.1002/abc','title':['Trial: reporting.']},{'DOI':'10.1002/def','title':['Trial reporting']},{'DOI':'10.1002/ghi','title':['Different title']}]
    r=title_candidates('Trial reporting',items)
    assert r['status']=='ambiguous_title_candidates'
    assert len(r['candidates'])==3 and r['qualified_identity'] is False
    assert title_candidates('Other',items)['status']=='no_exact_title_candidate'


def test_checkpoint_excludes_attempted_tasks_and_preserves_other_identities():
    c,l,s=fixture(); s['records'][2]['doi']='10.1002/different'; p=plan(c,l,s)
    first=select_tasks(p,2)
    second=select_tasks(p,12,[t['task_id'] for t in first])
    assert not {t['task_id'] for t in first}&{t['task_id'] for t in second}
    assert any(t['kind']=='doi' for t in second)
    with pytest.raises(ValueError):select_tasks(p,13)


def test_metadata_retains_locator_hints_but_no_automatic_reuse():
    record={'DOI':'10.1002/abc','link':[{'URL':'https://publisher.test/full?token=abc'},{'URL':'https://user:password@publisher.test/private'},{'URL':'file:///etc/passwd'}],'license':[{'URL':'https://creativecommons.org/licenses/by/4.0/'}]}
    r=metadata(record,'crossref','10.1002/abc')
    assert r['locator_hints']==['https://publisher.test/full']
    assert r['licence_hints']==['https://creativecommons.org/licenses/by/4.0/']
    assert r['rights']=='metadata_only_not_reuse_permission'
