import json
from pathlib import Path

import pytest

from scripts.evidence_deficit_replay import formal_controls
from scripts.evidence_verification import (
    assess, formal_verdict, gate, rerank_state, run,
)


def text(condition):
    return 'A report complies if and only if ' + condition + '.'


def test_formal_counterexamples_and_fail_closed_equivalence():
    controls = formal_controls()
    for row in controls:
        proof = formal_verdict(row['source'], row['candidate'], True)
        assert proof['relation'] == row['reference']
        assert gate('equivalent', True, proof) == (
            'equivalent' if row['reference'] == 'equivalent' else 'abstain'
        )
        assert bool(proof['counterexamples']) == (row['reference'] != 'equivalent')
    assert formal_verdict(text('alpha implies beta'), text('beta implies alpha'), False)['status'] == 'incomplete'
    for bad in ('alpha', 'alpha implies gamma', 'alpha implies beta. Extra clause', 'alpha is true and alpha is false'):
        assert gate('equivalent', True, formal_verdict(text(bad), text(bad), True)) == 'abstain'
    assert gate('broader', True, {'status': 'unsupported'}) == 'broader'
    assert gate('broader', False, {'status': 'unsupported'}) == 'abstain'


def test_assessment_blinds_labels_and_hidden_text():
    received = []

    def scorer(a, b):
        received.append((a, b))
        return (0.0, 1.0, 0.0)

    row = {'id': 'x', 'source': 'full source', 'evidence': {'x:head': 'visible', 'y:tail': 'distractor'}, 'parent_link': False, 'reference': 'equivalent', 'candidate': 'HIDDEN'}
    first = assess(row, {'minilm': scorer, 'deberta': scorer})
    assert received == [('full source', 'visible'), ('visible', 'full source')] * 2
    assert first['raw']['minilm']['prediction'] == 'equivalent'
    assert first['predictions']['strict_nli'] == 'abstain'
    assert first['predictions']['proof_required'] == 'abstain'
    row['reference'] = 'contradictory'
    row['candidate'] = 'OTHER HIDDEN'
    second = assess(row, {'minilm': scorer, 'deberta': scorer})
    assert first['predictions'] == second['predictions']
    row['evidence']['x:parent'] = 'full source'
    third = assess(row, {'minilm': scorer, 'deberta': scorer})
    assert third['predictions']['strict_nli'] == 'equivalent'
    assert third['predictions']['proof_required'] == 'abstain'


def test_fixed_pool_neural_reranking():
    row = {'id': 'x', 'source': 'query', 'evidence': {'x:head': 'first'}, 'pool': ['x:head', 'x:tail', 'y:tail'], 'parent_link': False}
    corpus = {'x:head': 'first', 'x:tail': 'missing qualifier', 'y:tail': 'distractor', 'z:tail': 'outside'}
    seen = []

    def ranker(a, b):
        seen.append(b)
        return float(b == 'missing qualifier')

    after, receipt = rerank_state(row, corpus, ranker)
    assert seen == ['first', 'missing qualifier', 'distractor']
    assert set(receipt['ranking']) == set(row['pool'])
    assert after['evidence']['x:tail'] == 'missing qualifier'
    assert 'z:tail' not in after['evidence']
    assert row['evidence'] == {'x:head': 'first'}
    with pytest.raises(ValueError, match='invalid provider relevance score'):
        rerank_state(row, corpus, lambda a, b: float('nan'))


def test_bounded_run_conserves_pairs_and_referrals():
    cases = json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']
    scorer = lambda a, b: (0.0, 1.0, 0.0)
    report = run(cases, {'minilm': scorer, 'deberta': scorer}, lambda a, b: 0.0)
    assert len(report['cases']) == 24
    assert report['summary']['head']['proof_required']['abstained'] == 24
    assert report['summary']['head']['strict_nli']['abstained'] == 24
    assert report['formal']['summary']['lexical']['false_equivalence'] == 3
    assert report['formal']['summary']['lexical_verified']['false_equivalence'] == 0
    assert report['formal']['summary']['formal']['correct'] == 4
    assert report['review_resolved'] == 0
    for row in report['cases']:
        assert set(row['neural_rerank']['ranking']) == set(row['pool'])
        assert row['split'] == 'test'


def test_fixture_pinning_and_unsupported_natural_text(tmp_path):
    from scripts.evidence_action_replay import FIXTURE_SHA
    from scripts.evidence_verification import pinned_fixture, truth_set

    path = Path('contracts/examples/semantic-reconciliation-synthetic-v1.json')
    assert len(pinned_fixture(path, FIXTURE_SHA)) == 36
    changed = tmp_path / 'bad.json'
    changed.write_text('{}')
    with pytest.raises(ValueError, match='fixture hash mismatch'):
        pinned_fixture(changed, FIXTURE_SHA)
    assert truth_set('A report complies if and only if alpha implies beta') is None
    assert truth_set('Report alpha.') is None
    assert truth_set(text('alpha is true or alpha is false')) == {0, 1, 2, 3}


def test_future_evidence_and_semantic_outcomes_cannot_change_initial_deficit_order():
    from scripts.evidence_deficit_replay import bind_predictions, replay
    from scripts import evidence_deficit_replay as module
    from scripts.evidence_action_replay import build_replay
    from unittest.mock import patch
    from copy import deepcopy
    from scripts.evidence_deficit_replay import digest

    cases = json.loads(Path("contracts/examples/semantic-reconciliation-synthetic-v1.json").read_text())["cases"]
    records = [dict(id=digest(json.dumps([c["id"], c["source"], c["candidate"]])), source_sha256=digest(c["source"]), candidate_sha256=digest(c["candidate"]), family=c["family"], split=c["split"], predictions={"minilm": "abstain", "deberta": "abstain"}) for c in cases]
    cache = bind_predictions(cases, records)
    observed = build_replay(cases)
    altered = deepcopy(observed)
    for row in altered:
        if row['split'] == 'test' and len(row['history']) == 2:
            row['evidence'] = {}
    test_ids = {c['id'] for c in cases if c['split'] == 'test'}
    changed = {k: (v[0], {m: 'equivalent' for m in v[1]}) if k in test_ids else v for k, v in cache.items()}
    first = replay(cases, cache)
    with patch.object(module, 'build_replay', return_value=altered):
        second = replay(cases, changed)
    for name in first['details']:
        assert {k: r['action'] for k, r in first['details'][name].items()} == {k: r['action'] for k, r in second['details'][name].items()}


def test_closed_grammar_exhaustive_against_bitmask_oracle():
    # Independent four-bit oracle: alpha is true in worlds 2 and 3, beta in 1 and 3.
    from itertools import product

    masks = {"alpha": 0b1100, "beta": 0b1010}
    expressions = {
        f"{a} implies {b}": ((~masks[a]) | masks[b]) & 0b1111
        for a, b in product(masks, repeat=2)
    }
    literals = {
        f"{atom} is {value}": mask if value == "true" else mask ^ 0b1111
        for atom, mask in masks.items()
        for value in ("true", "false")
    }
    for a, b in product(literals, repeat=2):
        expressions[f"{a} and {b}"] = literals[a] & literals[b]
        expressions[f"{a} or {b}"] = literals[a] | literals[b]
    assert len(expressions) == 36
    for (a, left), (b, right) in product(expressions.items(), repeat=2):
        if not left or not right:
            expected = "abstain"
        elif left == right:
            expected = "equivalent"
        elif not left & right:
            expected = "contradictory"
        elif left & right == right:
            expected = "narrower"
        elif left & right == left:
            expected = "broader"
        else:
            expected = "indeterminate"
        proof = formal_verdict(text(a), text(b), True)
        assert proof["relation"] == expected
        assert gate("equivalent", True, proof) == (
            "equivalent" if expected == "equivalent" else "abstain"
        )
        assert len(proof["counterexamples"]) == ((left ^ right).bit_count() if left and right else 0)
