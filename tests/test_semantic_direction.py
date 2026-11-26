import pytest

from scripts.five_class_benchmark import forms, legacy_to_rgi06, relation


@pytest.mark.parametrize("masks, expected", zip(forms(), [
    "equivalent", "broader", "narrower", "contradictory", "indeterminate"
], strict=True))
def test_legacy_b_relative_to_a_is_inverted_for_rgi06(masks, expected):
    a, b = masks
    original = relation(a, b)
    assert legacy_to_rgi06(original) == expected
    assert legacy_to_rgi06(original) == relation(b, a)
    assert legacy_to_rgi06(legacy_to_rgi06(original)) == original


def test_abstention_is_not_an_indeterminate_relation():
    assert legacy_to_rgi06("abstain") is None
    with pytest.raises(ValueError, match="unknown"):
        legacy_to_rgi06("unknown")
