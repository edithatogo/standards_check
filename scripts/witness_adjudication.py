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


CONDITIONS = {'P': 0b1100, 'Q': 0b1010, 'NOT_P': 0b0011, 'P_AND_Q': 0b1000}


def condition_vote(pair, vote):
    """Compile only independently selected controlled conditions, never infer a vote."""
    a, b = vote.get('a_condition'), vote.get('b_condition')
    left = CONDITIONS.get(a) if isinstance(a, str) else None
    right = CONDITIONS.get(b) if isinstance(b, str) else None
    label = relation(left, right) if left is not None and right is not None else 'abstain'
    if (set(vote) != {'a_condition', 'b_condition', 'a', 'b'} or
            any(not isinstance(vote.get(k), list) or 2 not in vote[k] for k in ('a', 'b'))):
        label = 'abstain'
    result = validate_index_vote(pair, {'label': label, 'a': vote.get('a'), 'b': vote.get('b')})
    return {**result, 'a_condition': a if left is not None else None,
            'b_condition': b if right is not None else None}
