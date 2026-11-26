import pytest
from tagging_followup import combine, count, validate_span


def test_missing_only_and_disagreement():
    text = 'except pilot studies'
    assert combine({}, {'exception': (0, 20)}) == {'exception': (0, 20)}
    assert combine({'exception': (0, 6)}, {'exception': (0, 20)}) == {'exception': (0, 6)}
    assert validate_span(text, (0, 20))
    assert not validate_span(text, (0, 21))
    assert not validate_span(text, (1, 1))


def test_absence_is_not_automatic_correctness():
    gold = [(0, 3), None, (5, 8), (0, 1)]
    predicted = [(0, 3), (2, 3), None, (0, 2)]
    result = count(gold, predicted)
    assert (result['tp'], result['fp'], result['fn'], result['tn']) == (1, 2, 2, 0)
    with pytest.raises(ValueError):
        count(gold, predicted[:-1])
