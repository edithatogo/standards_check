import pytest
from replay import fuse, choose, select, decision_metrics


def test_fusion_and_budget():
    assert fuse(['b', 'a'], ['a', 'c']) == ['a', 'b', 'c']
    assert select(['b', 'a', 'c'], lambda x: 0, 2) == {'a', 'b'}
    with pytest.raises(ValueError):
        fuse(['a', 'a'], [])


def test_gate_and_metrics():
    assert choose('abstain', 'broader') == 'broader'
    assert choose('equivalent', 'broader') == 'abstain'
    assert choose('equivalent', 'abstain') == 'equivalent'
    assert decision_metrics({'a': 'broader'}, {'a': 'equivalent'})['false_equivalence'] == 1
    with pytest.raises(ValueError):
        decision_metrics({'a': 'broader'}, {})
