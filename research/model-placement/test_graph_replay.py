import pytest
from graph_replay import graph, propagation, evaluate


def test_graph_from_unlabelled_rankings_and_isolated_vertices():
    g=graph([['a','b','c'],['a','b','d']],{'a','b','c','d','e'},k=2)
    assert g['a']=={'b':1.0}
    assert g['b']=={'a':1.0}
    assert g['e']=={'e':1.0}
    one,walk=propagation(['a','b','c','d','e'],g)
    assert sum(one.values())==pytest.approx(1)
    assert sum(walk.values())==pytest.approx(1)
    with pytest.raises(ValueError):graph([['a','a']],{'a','b'},k=2)


def test_fixed_pool_and_paired_gain_loss():
    q=('i','1'); ref={q:{'b'}}; before={q:['a','b']}; after={q:['b','a']}
    m=evaluate(ref,before,after,ks=(1,2),fixed=True)
    assert m['1']['gains']==1 and m['1']['losses']==0 and m['2']['gains']==0
    with pytest.raises(ValueError):evaluate(ref,before,{q:['b','c']},fixed=True)
