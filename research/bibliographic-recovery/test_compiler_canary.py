import pytest
from compiler_canary import assess, selected_jobs


def job():
    return {'strategy':{'strategy_id':'a','dialect':'crossref'},'strategy_sha256':'h','execution_authorized':False}


def test_compiler_receipt_never_grants_authority():
    compiled={'strategy_id':'a','dialect':'crossref','fidelity':'exact','review_required':False,'loss_codes':[],'warnings':[]}
    result=assess(job(),compiled)
    assert result['status']=='compiled_candidate_not_admitted'
    assert result['runtime_qualified'] is False and result['execution_authorized'] is False
    compiled['loss_codes']=['field-loss']
    assert assess(job(),compiled)['status']=='translation_review_required'
    compiled['strategy_id']='other'
    with pytest.raises(ValueError,match='binding'):assess(job(),compiled)


def test_selected_batch_strict_and_held():
    j=job();plan={'mechanism':'searchright','execution_status':'held_runtime_qualification','strategies':[j],'next_bounded_batch':['a']}
    assert selected_jobs(plan)==[j]
    plan['next_bounded_batch']=['a','a']
    with pytest.raises(ValueError):selected_jobs(plan)
    plan['next_bounded_batch']=['a'];j['execution_authorized']=True
    with pytest.raises(ValueError):selected_jobs(plan)
