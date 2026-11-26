import hashlib
import json
from pathlib import Path

import pytest

from searchright_recovery import gap_audit, plan_searches, compile_one, schema_registry


def fixtures():
    a = {'source_revision':'old','records':[{'id':'a','source_blob_sha':'x','status':'missing_identifier'}, {'id':'b','source_blob_sha':'y','status':'lookup_incomplete'}, {'id':'c','source_blob_sha':'z','status':'metadata_only'}, {'id':'d','source_blob_sha':'old','status':'missing_identifier'}]}
    b = {'source_revision':'new','records':[{'id':'a','source_blob_sha':'x','status':'missing_identifier'}, {'id':'b','source_blob_sha':'y','status':'lookup_incomplete'}, {'id':'c','source_blob_sha':'z','status':'metadata_only'}, {'id':'d','source_blob_sha':'new','status':'missing_identifier'}]}
    r = {'source_revision':'new','rows':[{'id':x['id'],'source_blob_sha':x['source_blob_sha'],'status':x['status'],'title':'Title '+x['id'],'route':route,'publication_identity':[],'link_identifier_candidates':{},'identity_conflict':False,'issuer_asset_candidates':[]} for x,route in zip(b['records'],['link_identifier_candidate','title_discovery_candidate','existing_identifier','issuer_asset_candidate'],strict=True)], 'observations':[]}
    r['rows'][0]['link_identifier_candidates']={'doi:10.1000/a': ['https://doi.org/10.1000/a']}
    r['rows'][3]['issuer_asset_candidates']=['https://example.test/checklist.pdf']
    return a,b,r


def test_persistent_same_blob_only_and_route_conservation():
    a,b,r=fixtures(); out=gap_audit(a,b,r)
    assert len(out['rows'])==4
    assert out['summary']['unchanged_catalogue_rows']==3
    assert out['summary']['persistent_identity_gaps']==2
    assert out['summary']['current_identity_gaps']==3
    assert out['summary']['persistent_routes']=={'link_identifier_candidate':1,'title_discovery_candidate':1}
    r['rows'][0]['source_blob_sha']='wrong'
    with pytest.raises(ValueError,match='binding'):gap_audit(a,b,r)


def test_searchright_plan_uses_native_ast_never_routes_assets_or_conflicts_to_search():
    a,b,r=fixtures();r['rows'][1]['identity_conflict']=True
    p=plan_searches(gap_audit(a,b,r),r)
    assert p['mechanism']=='searchright'
    assert p['execution_status']=='held_runtime_qualification'
    assert p['legacy_fallback'] is False
    assert len(p['strategies'])==2
    assert {x['strategy']['dialect'] for x in p['strategies']}=={'crossref','open_alex'}
    for x in p['strategies']:
        assert x['strategy']['query']['term']['fields']==['identifier']
        assert x['catalogue_ids']==['a']
        assert x['postfilter']['exact_identifier']=='doi:10.1000/a'
        assert x['execution_authorized'] is False
    assert {x['id']:x['route'] for x in p['non_search_rows']}=={'b':'identity_hold','d':'issuer_asset_candidate'}


def test_no_repeating_same_provider_route_and_near_match_is_candidate_only():
    a,b,r=fixtures();r['observations']=[{'kind':'title','value':'Title b','catalogue_ids':['b'],'observations':[{'provider':'crossref','result':{'status':'no_exact_title_candidate'}}]}]
    p=plan_searches(gap_audit(a,b,r),r)
    bplans=[x for x in p['strategies'] if 'b' in x['catalogue_ids']]
    assert {x['strategy']['dialect'] for x in bplans}=={'open_alex','pub_med','europe_pmc'}
    assert all(x['postfilter']['candidate_only'] for x in bplans)
    assert p['prior_attempts_excluded']==1


def test_compiler_rejects_unadmitted_binary_and_warned_output(tmp_path):
    a,b,r=fixtures(); job=plan_searches(gap_audit(a,b,r),r)['strategies'][0]
    binary=tmp_path/'searchright';binary.write_bytes(b'fake')
    with pytest.raises(ValueError,match='binary digest'):compile_one(job,binary,'0'*64,'independent-qualification-receipt',None)
    with pytest.raises(ValueError,match='qualification'):compile_one(job,binary,hashlib.sha256(b'fake').hexdigest(),'',None)


def test_schema_registry_blocks_external_resolution():
    # No network request is needed or permitted for unknown schema references.
    reg=schema_registry({'x':{'$id':'https://schemas.searchright.dev/x','type':'string'}})
    assert reg.contents('https://schemas.searchright.dev/x')['type']=='string'
    with pytest.raises(Exception):reg.get_or_retrieve('https://untrusted.invalid/schema')


def test_compile_preserves_review_required_and_never_authorizes_live(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from searchright_recovery import compile_one
    a,b,r=fixtures(); job=plan_searches(gap_audit(a,b,r),r)['strategies'][0]
    binary=tmp_path/'searchright';binary.write_bytes(b'qualified-fixture')
    output={'schema_version':'org.searchright.compiled-strategy.v1','strategy_id':job['strategy']['strategy_id'],'dialect':job['strategy']['dialect'],'query':'candidate query','warnings':[{'code':'test','message':'field loss','review_required':True}],'fidelity':'degraded','review_required':True,'loss_codes':['test'],'compilation_hash':'a'*64,'compiler_version':'synthetic-test'}
    def fake(args,**kwargs):
        assert args[0]==str(binary.resolve()) and args[1]=='compile'
        assert json.loads(Path(args[2]).read_bytes())==job['strategy']
        assert 'GH_TOKEN' not in kwargs['env'] and kwargs['timeout']==30
        return SimpleNamespace(stdout=json.dumps(output).encode())
    monkeypatch.setattr('searchright_recovery.subprocess.run',fake)
    validator=SimpleNamespace(validate=lambda _:None)
    result=compile_one(job,binary,hashlib.sha256(binary.read_bytes()).hexdigest(),'synthetic-qualification-only',validator)
    assert result['status']=='translation_review_required' and result['execution_authorized'] is False
    output['strategy_id']='mismatched'
    with pytest.raises(ValueError,match='binding'):compile_one(job,binary,hashlib.sha256(binary.read_bytes()).hexdigest(),'synthetic-qualification-only',validator)
