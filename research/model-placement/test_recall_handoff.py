import pytest
from recall_handoff import case_id, row, common_misses


def test_id_is_namespace_and_reference_bound_not_arm():
    a=case_id('E9','a'*64,['p',1])
    assert a==case_id('E9','a'*64,['p',1])
    assert a!=case_id('E10','a'*64,['p',1])
    assert a!=case_id('E9','b'*64,['p',1])


def test_stage_states_no_fake_success_or_cross_namespace():
    r=row('E9','synthetic','a'*64,['p',1],'flat',{'source_anchor':'fail'},'receipt',detail='corrupt')
    assert r['first_observed']==r['first_established']=='source_anchor'
    assert r['stages']['decision']=='unknown'
    with pytest.raises(ValueError): row('E9','synthetic','a'*64,['p',1],'flat',{'source_anchor':'bogus'},'receipt')


def test_common_misses_require_same_positive_ids():
    def arm(missed):
        return {'rows':[{'id':['f','1',t], 'stages':{'candidate_generation':'fail' if t in missed else 'pass'}} for t in ('a','b','c')]}
    audit={'arms':{'bge':arm({'a','b'}),'instructed_qwen_bge':arm({'b','c'})},'full_rankings':[{'id':['f','1'],'orders':{'bge':['a','c','b'],'instructed_qwen_bge':['c','a','b'],'exact_lexical':['b','a','c'],'exact_parent_topic_proxy':['a','b','c']}}]}
    result=common_misses(audit)
    assert result['n']==1
    assert result['records'][0]['original_id']==['f','1','b']
    audit['arms']['bge']['rows'].pop()
    with pytest.raises(ValueError): common_misses(audit)
