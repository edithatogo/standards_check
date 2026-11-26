import copy
import json
from pathlib import Path

import pytest

from scripts.evidence_action_replay import build_replay
from scripts.evidence_policy import choose, fit, policy_study, terminal
from scripts.evidence_deficit_replay import formal_controls


def test_terminal_gate_rejects_false_equivalence_and_preserves_true_one():
    for row in formal_controls():
        key = row['id']
        state = {'id': key, 'source': row['source'], 'evidence': {key + ':parent': row['candidate']}, 'parent_link': True}
        raw, gated, _ = terminal(state)
        assert raw == 'equivalent'
        assert gated == ('equivalent' if row['reference'] == 'equivalent' else 'abstain')


def test_training_and_initial_policy_are_immune_to_heldout_outcome_mutation():
    cases = json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']
    rows = build_replay(cases)
    changed = copy.deepcopy(rows)
    for row in changed:
        if row['split'] == 'test':
            row['reference'] = 'equivalent' if row['reference'] != 'equivalent' else 'contradictory'
            if row['history']:
                row['evidence'] = {}
    for mode in ('bandit', 'fitted_q'):
        first = fit(rows, mode, 2, 0.1, False)
        second = fit(changed, mode, 2, 0.1, False)
        for row in rows:
            if row['split'] == 'test' and not row['history']:
                assert choose(row, first, 2, False) == choose(row, second, 2, False)
                assert choose(row, first, 2, False) != 'parent' or row['parent_link']


def test_policy_study_conserves_budget_referrals_and_gate():
    cases = json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']
    report = policy_study(build_replay(cases))
    for mode, arms in report['comparisons'].items():
        assert {len(arm['cases']) for arm in arms.values()} == {24}
        assert len({arm['referrals'] for arm in arms.values()}) == 1
        for arm in arms.values():
            assert arm['review_resolved'] == 0
            assert arm['calls'] <= 48
            if mode == 'exact_two':
                assert arm['calls'] == 48
            assert all(len(row['history']) == len(set(row['history'])) for row in arm['cases'])
            assert all(row['gated_prediction'] != 'equivalent' for row in arm['cases'])
    with pytest.raises(ValueError, match='mode'):
        fit(build_replay(cases), 'unknown', 2, .1, False)


def test_oracle_is_separate_upper_bound_and_cli_pins_fixture(tmp_path, monkeypatch):
    from scripts import evidence_policy as module

    output = tmp_path / 'policy.json'
    monkeypatch.setattr('sys.argv', ['policy', '--output', str(output)])
    module.main()
    report = json.loads(output.read_text())
    assert report['admission'] == 'advisory_only'
    for name, oracle in report['hindsight_ceiling'].items():
        assert oracle['uses_heldout_labels'] is True
        assert oracle['reward'] >= max(a['reward'] for a in report['comparisons'][name].values()) - 1e-10
    bad = tmp_path / 'bad.json'
    bad.write_text('{}')
    monkeypatch.setattr('sys.argv', ['policy', '--fixture', str(bad), '--output', str(output)])
    with pytest.raises(ValueError, match='fixture'):
        module.main()


def test_follow_rejects_illegal_or_missing_action_and_mismatched_replay():
    from scripts.evidence_policy import follow

    cases = json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']
    rows = build_replay(cases)
    lookup = {(r['id'], tuple(r['history'])): r for r in rows}
    root = next(r for r in rows if not r['history'] and not r['parent_link'])
    with pytest.raises(ValueError, match='unavailable'):
        follow(root, lookup, 2, lambda _: 'parent')
    bad = {**root, 'transitions': {**root['transitions'], 'expand': {**root['transitions']['expand'], 'next': ['parent']}}}
    with pytest.raises(ValueError, match='transition'):
        follow(bad, lookup, 2, lambda _: 'expand')
    with pytest.raises(ValueError, match='duplicate'):
        policy_study(rows + [root])
    other = copy.deepcopy(rows)
    next(r for r in other if r['history'])['family'] = 'unexpected'
    with pytest.raises(ValueError, match='identity'):
        policy_study(other)


def test_parent_first_comparator_preserves_original_arms_and_gate():
    cases = json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']
    rows = build_replay(cases)
    baseline = policy_study(rows)
    expanded = policy_study(rows, compare_parent_first=True)
    roots = {r['id']: r for r in rows if not r['history']}
    for name, arms in expanded['comparisons'].items():
        parent = arms.pop('parent_first')
        assert arms == baseline['comparisons'][name]
        assert parent['gated_false_equivalence'] == 0
        assert parent['missed_equivalence'] == 8
        assert parent['referrals'] == 6 and parent['review_resolved'] == 0
        assert len(parent['cases']) == 24
        assert all(
            row['history'][0] == ('parent' if roots[row['id']]['parent_link'] else 'expand')
            for row in parent['cases']
        )
        if name == 'exact_one':
            assert (parent['complete'], parent['gated_correct'], parent['calls'], parent['reranks']) == (23, 14, 24, 0)
            assert parent['hindsight_regret'] == pytest.approx(0)
    assert expanded == baseline
