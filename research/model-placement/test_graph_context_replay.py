import pytest
from graph_context_replay import contextualize, fixed_pool, paired, run


def test_context_is_only_parent_text_and_preserves_identity():
    target = {'A': 'report outcome', 'B': 'report date'}
    assert contextualize(target, {'A':'H1','B':'H1'}, {'H1':'Trial'}) == {'A':'Trial\nreport outcome','B':'Trial\nreport date'}
    with pytest.raises(ValueError):
        contextualize(target, {'A':'H1'}, {'H1':'Trial'})
    with pytest.raises(ValueError):
        contextualize(target, {'A':'H1','B':'H2'}, {'H1':'Trial'})


def test_fixed_pool_and_paired_counts():
    base = {('f','q'): ['A','B']}
    after = fixed_pool(base, {('f','q'):{'A':0.0,'B':0.9,'C':1.0}})
    assert after == {('f','q'): ['B','A']}
    assert paired({('f','q'):{'B','C'}}, base, after, k=1) == {'gains':1,'losses':0,'hits':1,'macro_query_recall':.5,'precision':1.0,'returned_slots':1}
    with pytest.raises(ValueError):
        fixed_pool(base, {('f','q'):{'A':.1}})


def test_artifact_digest_rejects_unqualified(tmp_path):
    p=tmp_path/'bad.zip'; p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='artifact digest'):
        run(p,tmp_path/'missing.json')
