import pytest
from qualifier_replay import complete, metrics, overlap_match, run


def test_completion_preserves_operator_and_checks_kind():
    text = 'For trials, report A unless exempt.'
    rule = [('applicability', 0, 10), ('exception', 21, 34)]
    assert complete(text, [('applicability', 4, 10)], rule) == [('applicability', 0, 10)]
    assert complete(text, [('condition', 4, 10)], rule) == [('condition', 4, 10)]
    assert complete(text, [('applicability', 4, 10)], rule, guarded=True) == [('applicability', 0, 10)]
    assert complete(text, [('condition', 4, 10)], rule, guarded=True) == []
    with pytest.raises(ValueError):
        complete(text, [('condition', -1, 10)], rule)


def test_exact_and_overlap_one_to_one():
    gold = [('condition', 0, 10), ('condition', 12, 20)]
    pred = [('condition', 4, 8), ('condition', 5, 9), ('exception', 12, 20)]
    assert overlap_match(gold, pred) == 1
    assert metrics(gold, pred)['tp'] == 0
    assert metrics(gold, pred, overlap=True)['fp'] == 2
    assert metrics(gold, pred, overlap=True)['fn'] == 1


def test_unqualified_receipt_rejected(tmp_path):
    path = tmp_path / 'unqualified.zip'
    path.write_bytes(b'not an artifact')
    with pytest.raises(ValueError, match='digest mismatch'):
        run(path)
