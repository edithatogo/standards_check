import copy
import pytest
from recall_handoff import case_id, digest
from locked_join import join_locked


def controls():
    cases=[{'namespace':'synthetic-join-control','original_id':['f','1','t'],'family_component':'family-a','split':'evaluation','source_anchor':'p1/item1','target_anchor':'p2/item2','candidate_budget':10,'review_budget':5,'required_components':['c1','c2']}]
    lock={'reference_tier':'synthetic_author_labelled','reference_ledger_receipt':'synthetic-test','eligible_universe_digest':'1'*64,'cases':cases,'arms':['arm']}
    pin=digest(lock); ident=case_id(cases[0]['namespace'],pin,cases[0]['original_id'])
    def packet(owner,stages,**extra):
        return {'reference_lock_digest':pin,'owner':owner,'rows':[{'case_id':ident,'arm':'arm','receipt':'synthetic-'+owner,'stages':stages,**extra}]}
    return lock,pin,packet


def test_missing_stage_unknown_and_complete_bundle():
    lock,pin,p=controls()
    packets=[p('layout',{'source_anchor':'pass'}),p('coordinator',{'candidate_generation':'pass','rank_cutoff':'pass'}),p('offline',{'evidence':'pass'})]
    r=join_locked(lock,pin,packets)['rows'][0]
    assert r['first_established']=='unresolved' and r['stages']['decision']=='unknown'
    packets.append(p('orthogonal',{'decision':'pass'},decision_detail='accepted',covered_components=['c1','c2']))
    assert join_locked(lock,pin,packets)['rows'][0]['first_established']=='none'
    packets[-1]['rows'][0]['covered_components']=['c1']
    with pytest.raises(ValueError,match='bundle'):join_locked(lock,pin,packets)


def test_reject_wrong_owner_conflict_or_unknown_case():
    lock,pin,p=controls()
    with pytest.raises(ValueError,match='owner'):join_locked(lock,pin,[p('offline',{'decision':'pass'})])
    with pytest.raises(ValueError,match='conflict'):join_locked(lock,pin,[p('layout',{'source_anchor':'pass'}),p('layout',{'source_anchor':'fail'})])
    wrong=p('layout',{'source_anchor':'pass'});wrong['rows'][0]['case_id']='wrong'
    with pytest.raises(ValueError,match='case'):join_locked(lock,pin,[wrong])
    with pytest.raises(ValueError,match='digest'):join_locked(lock,'0'*64,[])


def test_family_overlap_and_no_fake_resolution():
    lock,pin,p=controls(); a=copy.deepcopy(lock['cases'][0]);a['original_id']=['f','3','u'];a['split']='calibration';lock['cases'].append(a)
    with pytest.raises(ValueError,match='family'):join_locked(lock,digest(lock),[])
    lock,pin,p=controls()
    with pytest.raises(ValueError,match='resolution'):join_locked(lock,pin,[p('orthogonal',{'decision':'pass'},decision_detail='referral_resolved',covered_components=['c1','c2'])])


def test_independent_gate_is_not_inferred_from_synthetic():
    lock,pin,p=controls()
    r=join_locked(lock,pin,[])
    assert r['independent_positive_count']==0 and r['scientific_qualification'] is False
    lock['reference_tier']='independently_adjudicated'
    with pytest.raises(ValueError,match='qualification'):join_locked(lock,digest(lock),[])


def test_join_preserves_candidate_and_review_ranks():
    lock,pin,p=controls()
    packet=p('coordinator',{'candidate_generation':'pass','rank_cutoff':'fail'},candidate_rank=2,review_rank=7)
    r=join_locked(lock,pin,[packet])['rows'][0]
    assert (r['candidate_rank'],r['review_rank'])==(2,7)
    packet['rows'][0]['review_rank']=3
    with pytest.raises(ValueError,match='rank'):join_locked(lock,pin,[packet])
