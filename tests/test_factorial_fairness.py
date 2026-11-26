import json
from pathlib import Path

import pytest

from scripts.factorial_fairness import (
    controlled, full_design, coverage_ledger, paired_bayes, predict_grouped,
)

FIXTURE = Path('contracts/examples/semantic-reconciliation-synthetic-v1.json')


def test_controlled_has_equal_pool_and_new_evidence_budgets():
    rows = json.loads(FIXTURE.read_text())['cases']
    cells, features = controlled(rows)
    assert len(cells) == 8 and len(features) == 36
    for cell in cells.values():
        assert len(cell) == 36
        for row in cell.values():
            assert len(row['pool']) == 6
            assert len(row['selected']) == 2
            assert set(row['selected']) <= set(row['pool'])
            assert row['id'] + ':head' not in row['pool']
            assert row['complete'] <= row['target_in_pool']
    for a in ('00', '01', '10', '11'):
        for key in features:
            assert cells[a+'0'][key]['pool'] == cells[a+'1'][key]['pool']


def test_full_design_and_ledger_never_fabricate_execution():
    design = full_design()
    assert len(design) == len(set(design)) == 64
    assert design[0] == '000000' and design[-1] == '111111'
    rows = [{'id': 'equator:prisma', 'source_blob_sha': 'a'*40},
            {'id': 'equator:other', 'source_blob_sha': 'b'*40}]
    ledger = coverage_ledger(rows)
    assert ledger['total_slots'] == 128
    assert ledger['executed_slots'] == 0
    assert ledger['rows'][0]['cells'][0]['status'] == 'held_source_or_component_qualification'
    assert all(c['status'].startswith('held_') for row in ledger['rows'] for c in row['cells'])
    with pytest.raises(ValueError, match='duplicate'):
        coverage_ledger(rows + rows)


def test_bayesian_bootstrap_constant_and_grouped_predictions():
    cells = {'0': {'a': {'family': 'A', 'complete': 0}, 'b': {'family': 'B', 'complete': 0}},
             '1': {'a': {'family': 'A', 'complete': 1}, 'b': {'family': 'B', 'complete': 1}}}
    out = paired_bayes(cells, ['factor'], 'complete', draws=100)
    assert out['factor']['mean'] == pytest.approx(1)
    assert out['factor']['interval_90'] == pytest.approx([1, 1])
    result = predict_grouped(cells, {'a': [0], 'b': [1]}, models=('beta',))
    assert len(result['folds']) == 2
    assert result['metrics']['beta']['n'] == 4
    with pytest.raises(ValueError, match='paired'):
        paired_bayes({'0': cells['0'], '1': {'a': cells['1']['a']}}, ['factor'], 'complete')


def test_hierarchical_prediction_is_finite_and_held_family_not_fit():
    import numpy as np
    from scripts.factorial_fairness import hierarchical_predict

    x = np.asarray([[0.], [1.], [0.], [1.]])
    y = np.asarray([0, 1, 0, 1])
    p = hierarchical_predict(x, y, ['A', 'A', 'B', 'B'], ['a', 'a', 'b', 'b'], x[:2])
    assert (0 < p).all() and (p < 1).all()
    assert p[1] > p[0]


def test_neural_rank_comparison_matches_pool_and_budget():
    from scripts.factorial_fairness import observed_neural_ranking

    cases = json.loads(FIXTURE.read_text())['cases']
    row = cases[0]
    key = row['id']
    other = next(c for c in cases if c['family'] == row['family'] and c['id'] != key)['id']
    pool = [key + ':head', key + ':tail', other + ':head', other + ':tail']
    report = {'cases': [{'id': key, 'family': row['family'], 'pool': pool,
                         'states': {'expanded': {'evidence_ids': [key + ':head'], 'complete': False}},
                         'neural_rerank': {'scores': dict(zip(pool, [4, 3, 2, 1], strict=True))}}]}
    result = observed_neural_ranking(cases, report)
    item = result['rows'][0]
    assert item['neural']['selected'][0] == key + ':tail'
    assert len(item['lexical']['selected']) == len(item['neural']['selected']) == 2
    assert item['neural']['complete']
    report['cases'][0]['neural_rerank']['scores'].pop(pool[0])
    with pytest.raises(ValueError, match='pool'):
        observed_neural_ranking(cases, report)


def test_cli_and_rank(tmp_path, monkeypatch):
    from scripts import factorial_fairness as module

    assert module.design_rank() == 64
    out = tmp_path / 'output.json'
    monkeypatch.setattr('sys.argv', ['factorial', '--fixture', str(FIXTURE), '--output', str(out)])
    module.main()
    report = json.loads(out.read_text())
    assert report['heldout_summary']['101']['complete'] == 20
    assert report['heldout_resource_counts']['101']['new_fragments'] == 48
    bad = tmp_path / 'bad.json'
    bad.write_text('{}')
    with pytest.raises(ValueError, match='unqualified'):
        module.read_pinned(bad, module.FIXTURE_SHA)


def test_proof_coverage_is_matched_without_using_reference_for_ranking():
    from scripts.factorial_fairness import matched_coverage

    def row(key, confidence, proof, reference):
        state = {'predictions': {'strict_nli': 'equivalent', 'proof_required': proof},
                 'raw': {'nli': {'forward': [confidence], 'reverse': [confidence]}}}
        return {'id': key, 'reference': reference, 'states': {'rule_terminal': state}}
    a = row('a', 0.9, 'abstain', 'equivalent')
    b = row('b', 0.8, 'equivalent', 'contradictory')
    report = matched_coverage({'cases': [a, b]})['rule_terminal']
    assert report['matched_confidence_advisory']['ids'] == ['a']
    assert report['matched_confidence_advisory']['accepted'] == report['proof_required']['accepted'] == 1
    a['reference'] = 'contradictory'
    assert matched_coverage({'cases': [a, b]})['rule_terminal']['matched_confidence_advisory']['ids'] == ['a']
