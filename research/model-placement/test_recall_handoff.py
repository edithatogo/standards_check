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


def test_tagger_followup_preserves_locked_positive_ids_and_rejects_drift(tmp_path, monkeypatch):
    import json
    import zipfile
    import hashlib
    from recall_handoff import append_tagger_followup, PINS

    fixture = 'b'*64
    c = {'id':'q1','family':'f','text':'If so','expected':[['condition',0,5]],'predicted':[['condition',0,5]],'invalid_abstention':None}
    baseline = [row('E10','synthetic_author_labelled',fixture,['q1','condition',0,5],'rules',{'source_anchor':'pass'},'original',family='f',source_text_digest=__import__('recall_handoff').digest(c['text']),observed_spans=c['predicted'])]
    path = tmp_path/'github-actions-artifact-15107111276.zip'
    def archive(changed=False):
        missing={**c,'predicted':[]}
        with zipfile.ZipFile(path,'w') as z:
            for arm in ('clause','per_type'):
                z.writestr(arm+'.json',json.dumps({'fixture_sha256':fixture,'evaluation':{'cases':[missing if not changed else {**missing,'expected':[['condition',1,5]]}]}}))
            z.writestr('supervised.json',json.dumps({'fixture_sha256':fixture,'arms':{'rules':{'cases':[c]},'token_bio':{'cases':[missing]},'span_boundary':{'cases':[missing]}}}))
        monkeypatch.setitem(PINS,15107111276,hashlib.sha256(path.read_bytes()).hexdigest())
    archive()
    result=append_tagger_followup(tmp_path,baseline)
    assert len(result)==4
    assert {r['case_id'] for r in result}=={baseline[0]['case_id']}
    assert all(r['stages']['source_anchor']=='fail' for r in result)
    archive(True)
    with pytest.raises(ValueError,match='reference'):append_tagger_followup(tmp_path,baseline)
