import pytest

from fixed_pool import fixed_pools, score_pool


def test_fusion_and_full_universe():
    q = ('instrument', 'one')
    bge = {q: ['a', 'b', 'c', 'd']}
    char = {q: ['d', 'c']}
    arms = fixed_pools(bge, char, {'a', 'b', 'c', 'd'}, budget=2)
    assert arms['bge'][q] == ['a', 'b']
    assert arms['fused'][q] == ['d', 'c']
    with pytest.raises(ValueError, match='universe'):
        fixed_pools({q: ['a', 'b', 'c']}, char, {'a', 'b', 'c', 'd'}, budget=2)
    with pytest.raises(ValueError, match='duplicate'):
        fixed_pools(bge, {q: ['d', 'd']}, {'a', 'b', 'c', 'd'}, budget=2)


def test_scores_only_fixed_pool_no_reference_or_id_inference():
    q = ('instrument', 'one')
    calls = []

    def scorer(query, target):
        calls.append((query, target))
        return 0.5

    ranked, rows = score_pool({q: 'topic'}, {'a': 'alpha', 'b': 'beta', 'c': 'gamma'}, {q: ['b', 'a']}, scorer, budget=2)
    assert ranked[q] == ['a', 'b']
    assert calls == [('topic', 'beta'), ('topic', 'alpha')]
    assert rows[0]['pool'] == ['b', 'a']
    assert rows[0]['scores'] == {'b': 0.5, 'a': 0.5}
    with pytest.raises(ValueError, match='nonfinite'):
        score_pool({q: 'topic'}, {'a': 'alpha', 'b': 'beta'}, {q: ['b', 'a']}, lambda *_: float('nan'), budget=2)
    with pytest.raises(ValueError, match='pool'):
        score_pool({q: 'topic'}, {'a': 'alpha', 'b': 'beta'}, {q: ['b', 'b']}, scorer, budget=2)
    assert len(calls) == 2
