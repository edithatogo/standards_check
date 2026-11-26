import pytest
from evidence_budget import expand, allocation, gains


def test_expansion_conserves_initial_and_budget():
    k=('i','1'); first={k:['a','b']}; full={k:['b','c','a','d','e']}
    assert expand(first,full,{k},extra=2)=={k:['a','b','c','d']}
    assert expand(first,full,set(),extra=2)==first
    with pytest.raises(ValueError):
        expand(first,{k:['a','b','c']},{k},extra=2)


def test_allocation_independent_of_references_and_grouped():
    a=('i','1'); b=('i','2'); c=('j','1'); d=('j','2')
    ids=[a,b,c,d]; priorities={a:0,b:1,c:0,d:1}
    assert allocation(ids,priorities,50)=={b,d}
    assert gains({a:{'a'},b:{'b'}},{a:['c'],b:['b']},{a:['c','a'],b:['b']})==(1,0)
