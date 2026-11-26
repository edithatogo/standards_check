import copy

import pytest

from scripts.evidence_replay_diagnostics import audit, select_new


def test_selection_conserves_order_and_budget():
    assert select_new(['a', 'b', 'c', 'd'], {'a', 'c'}, 2) == ['b', 'd']
    assert select_new(['a', 'b'], {'a'}, 4) == ['b']
    assert select_new(['a'], {'a'}, 1) == []
    for order, limit in [(['a', 'a'], 1), (['a'], 0), (['a'], True)]:
        with pytest.raises(ValueError):
            select_new(order, set(), limit)


def test_audit_distinguishes_pool_loss_rank_loss_and_redundant_slots():
    def case(key, ranking, complete=False):
        seen = [key + ':head'] + ([key + ':tail'] if complete else [])
        state = {'evidence_ids': seen, 'complete': complete,
                 'predictions': {'minilm': 'equivalent', 'deberta': 'equivalent',
                                 'strict_nli': 'equivalent' if complete else 'abstain'}}
        return {'id': key, 'family': 'F', 'reference': 'indeterminate',
                'pool': list(ranking), 'states': {'expanded': state, 'head': state,
                                           'rule_terminal': state},
                'lexical_rerank': {'ranking': list(ranking)}, 'neural_rerank': {'ranking': list(ranking)}}
    rows = [case('x', ['x:head', 'a:head', 'x:tail']),
            case('y', ['y:head', 'a:head', 'a:tail']),
            case('z', ['z:head', 'z:tail'], True)]
    report = audit({'cases': rows})
    assert report['expanded_complete'] == 1
    assert report['missing_outside_pool'] == 1
    assert report['missing_inside_pool'] == 1
    assert report['arms']['expanded']['lexical_rerank']['2']['complete_pairs'] == 2
    assert report['arms']['expanded']['lexical_rerank']['2']['gained_ids'] == ['x']
    assert report['agreement']['expanded']['shared_wrong_incomplete'] == 2
    assert report['agreement']['expanded']['shared_wrong_complete'] == 1
    broken = copy.deepcopy(rows)
    broken[0]['neural_rerank']['ranking'].append('outside')
    with pytest.raises(ValueError, match='outside'):
        audit({'cases': broken})
    with pytest.raises(ValueError, match='unique'):
        audit({'cases': [rows[0], rows[0]]})


def test_cli_pins_input_and_duplicate_pool_fails(tmp_path, monkeypatch):
    import hashlib
    import json
    from scripts import evidence_replay_diagnostics as module

    state = {'evidence_ids': ['x:head'], 'complete': False,
             'predictions': {'minilm': 'abstain', 'deberta': 'broader'}}
    row = {'id': 'x', 'reference': 'indeterminate', 'pool': ['x:head'],
           'states': {name: state for name in ('head', 'expanded', 'rule_terminal')},
           'lexical_rerank': {'ranking': ['x:head']}, 'neural_rerank': {'ranking': ['x:head']}}
    bad = {**row, 'pool': ['x:head', 'x:head']}
    with pytest.raises(ValueError, match='duplicate pool'):
        module.audit({'cases': [bad]})
    with pytest.raises(ValueError, match='unique'):
        module.audit({'cases': []})
    source, output = tmp_path / 'input.json', tmp_path / 'output.json'
    source.write_text(json.dumps({'cases': [row]}))
    monkeypatch.setattr('sys.argv', ['audit', '--report', str(source), '--output', str(output)])
    with pytest.raises(ValueError, match='unqualified'):
        module.main()
    monkeypatch.setattr(module, 'REPORT_SHA256', hashlib.sha256(source.read_bytes()).hexdigest())
    module.main()
    assert json.loads(output.read_text())['missing_outside_pool'] == 1
