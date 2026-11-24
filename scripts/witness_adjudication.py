"""Derive a five-class judgement from independently selected compliant scenarios."""
from .five_class_benchmark import relation, validate_index_vote


def witness_mask(values):
    if (not isinstance(values, list) or not values or
            any(type(v) is not int or not 1 <= v <= 4 for v in values) or
            len(set(values)) != len(values)):
        return None
    return sum(1 << (v - 1) for v in values)


def witness_label(a, b):
    left, right = witness_mask(a), witness_mask(b)
    return relation(left, right) if left is not None and right is not None else 'abstain'


def control_input(pair):
    prefix = 'In this controlled example the two reporting checks are independent.\n'
    return pair['source'].startswith(prefix) and pair['candidate'].startswith(prefix)


def witness_vote(pair, vote):
    a, b = vote.get('a_compliant'), vote.get('b_compliant')
    label = witness_label(a, b)
    if set(vote) != {'a_compliant', 'b_compliant', 'a', 'b'}:
        label = 'abstain'
    result = validate_index_vote(pair, {'label': label, 'a': vote.get('a'), 'b': vote.get('b')})
    return {**result, 'a_compliant': a if witness_mask(a) is not None else None,
            'b_compliant': b if witness_mask(b) is not None else None}
