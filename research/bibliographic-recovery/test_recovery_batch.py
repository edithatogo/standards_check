from recovery_batch import choose_batch, summarize_batch
import pytest


def job(i, provider, ids, persistent=None, kind='doi', value=None):
    return {'strategy': {'strategy_id': i, 'dialect': provider, 'query': {'term': {'text': value or i}}}, 'kind': kind, 'catalogue_ids': ids, 'persistent_ids': ids if persistent is None else persistent, 'execution_authorized': False}


def test_prefers_distinct_ids_over_duplicate_provider_work():
    jobs = [job('a','crossref',['a','b'],value='shared'),job('b','open_alex',['a','b'],value='shared'),job('c','open_alex',['c']),job('d','crossref',['d'])]
    batch=choose_batch(jobs, budget=2, provider_limit=1)
    assert batch==['a','c']
    assert summarize_batch(jobs,batch)['persistent_ids']==3
    assert choose_batch(list(reversed(jobs)),budget=2,provider_limit=1)==batch


def test_bounds_and_conflicts():
    jobs=[job('a','crossref',['a']),job('b','crossref',['b'])]
    assert len(choose_batch(jobs,budget=8,provider_limit=1))==1
    with pytest.raises(ValueError): choose_batch(jobs+[jobs[0]])
    with pytest.raises(ValueError): choose_batch(jobs,budget=9)
    with pytest.raises(ValueError): summarize_batch(jobs,['a','a'])
    jobs[0]['execution_authorized']=True
    with pytest.raises(ValueError): choose_batch(jobs)


def test_prior_exact_leads_lower_priority_not_removed():
    jobs = [job('a','crossref',['a','b']),job('b','crossref',['c']),job('c','open_alex',['a'])]
    assert choose_batch(jobs,budget=1,already_observed=['a','b'])==['b']
    assert len(choose_batch(jobs,budget=3,already_observed=['a','b']))==3
