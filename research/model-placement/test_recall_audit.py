import pytest
from recall_audit import first_failure, stage_counts, audit_arm, exact_phrase, parent_topics, rrf_rank


def test_unknown_preceding_failure_is_not_causal_attribution():
    states = dict(zip(('source_anchor','candidate_generation','rank_cutoff','evidence','decision'), ('unknown','fail','not_reached','unknown','unknown')))
    assert first_failure(states) == ('candidate_generation', 'unresolved')
    states['source_anchor'] = 'pass'
    assert first_failure(states) == ('candidate_generation', 'candidate_generation')
    states['source_anchor'] = 'fail'
    assert first_failure(states) == ('source_anchor', 'source_anchor')
    totals = stage_counts([{'stages': states}])
    assert totals['overlap']['source_anchor|candidate_generation'] == {'both_failed':1,'both_observed':1}
    assert totals['overlap']['source_anchor|evidence']['both_observed'] == 0


def test_pool_and_review_are_distinct_and_losses_retained():
    refs={('f','1'):{'a','c'}}; pool={('f','1'):['a','b','d']}; rank={('f','1'):['b','a','d']}
    result=audit_arm(refs,pool,rank,review=1,pool_budget=3)
    assert result['metrics']['pool']['hits']==1
    assert result['metrics']['review']['hits']==0
    assert result['failure_counts']['first_observed']=={'candidate_generation':1,'rank_cutoff':1}
    assert result['failure_counts']['first_established']=={'unresolved':2}
    with pytest.raises(ValueError,match='pool'):
        audit_arm(refs,pool,{('f','1'):['a','b','c']},review=1,pool_budget=3)


def test_phrase_boundary_and_parent_proxy():
    assert exact_phrase('Price year','The price year, and index.')
    assert not exact_phrase('cost','costing')
    assert not exact_phrase('', 'anything')
    q={('f','2'):'scope',('f','2.1'):'cost',('f','2.1.1'):'price',('g','2.1'):'other'}
    assert parent_topics(q)=={('f','2.1'):'scope',('f','2.1.1'):'cost'}
    assert rrf_rank({'a','b','c'},[['b'],['c']],{'a'})==['a','b','c']
    with pytest.raises(ValueError): rrf_rank({'a','b'},[['a','a']],set())
