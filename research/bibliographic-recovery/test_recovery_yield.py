import pytest
from recovery_yield import report, aggregate


def test_overlap_unknown_and_failure_cost():
    records=[{'provider':'p','kind':'doi','value':'10.1000/x','ids':['a','b'],'status':'exact_doi_metadata','seconds':2.0,'response_bytes':10,'work_ids':['doi:10.1000/x']}, {'provider':'q','kind':'doi','value':'10.1000/x','ids':['a'],'status':'exact_doi_metadata','seconds':1.0,'response_bytes':5,'work_ids':['doi:10.1000/x']}, {'provider':'p','kind':'pmid','value':'2','ids':['c'],'status':'lookup_incomplete','seconds':4.0,'response_bytes':None,'work_ids':[]}]
    m=aggregate(records)
    assert m['requests']==3 and m['exact_responses']==2 and m['unique_work_ids']==1
    assert m['catalogue_ids_with_exact_response']==2 and m['observed_request_seconds']==7
    assert m['response_bytes_observed']==15 and m['responses_with_byte_count']==2
    assert m['seconds_per_distinct_work_lead']==7
    assert m['qualified_editions']==0
    assert aggregate([])['seconds_per_distinct_work_lead'] is None


def test_identity_mismatch_rejected():
    c={'source_revision':'r','guidelines':[{'id':'a','source_blob_sha':'s','study_types':['x'],'acronym':'A'}]}
    receipt={'source_revision':'r','rows':[{'id':'a','source_blob_sha':'s','route':'link_identifier_candidate'}],'observations':[{'kind':'doi','value':'10.1000/x','catalogue_ids':['a'],'observations':[{'provider':'crossref','result':{'status':'exact_doi_metadata','doi':'10.1000/y'},'seconds':1}]}]}
    with pytest.raises(ValueError,match='identity'):report(c,receipt)
