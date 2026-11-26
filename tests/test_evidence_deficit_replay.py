import hashlib
import json
from pathlib import Path

import pytest

from scripts.evidence_action_replay import build_replay
from scripts.evidence_deficit_replay import digest, bind_predictions, replay, visible_candidate


def fixture():
    return json.loads(Path('contracts/examples/semantic-reconciliation-synthetic-v1.json').read_text())['cases']


def records(cases):
    return [dict(id=digest(json.dumps([c['id'], c['source'], c['candidate']])),
                 source_sha256=digest(c['source']), candidate_sha256=digest(c['candidate']),
                 family=c['family'], split=c['split'],
                 predictions={'minilm': 'abstain', 'deberta': 'abstain'}) for c in cases]


def test_cache_rejects_bad_pair_hash_and_missing_coverage():
    cases = fixture()
    rows = records(cases)
    assert len(bind_predictions(cases, rows)) == 36
    with pytest.raises(ValueError, match='coverage'):
        bind_predictions(cases, rows[:-1])
    rows[0]['source_sha256'] = 'wrong'
    with pytest.raises(ValueError, match='identity'):
        bind_predictions(cases, rows)


def test_incomplete_evidence_never_reconstructs_hidden_text():
    rows = build_replay(fixture())
    assert all(visible_candidate(row) is None for row in rows if not row['history'])
    assert any(visible_candidate(row) is not None for row in rows if row['history'])


def test_matched_budget_and_no_heldout_label_leakage():
    cases = fixture()
    cache = bind_predictions(cases, records(cases))
    a = replay(cases, cache)
    mutated = [{**c, 'forward': 'contradiction', 'reverse': 'contradiction'} if c['split'] == 'test' else c for c in cases]
    b = replay(mutated, cache)
    for name in a['arms']:
        assert a['details'][name] == b['details'][name]
        assert a['arms'][name]['review_resolved'] == 0
        if name.startswith(('fixed_', 'deficit_', 'learned_')):
            assert a['arms'][name]['semantic_calls'] == 4
            assert a['arms'][name]['retrieval_calls'] == 44
    assert len({v['referrals'] for v in a['arms'].values()}) == 1


def test_load_pinned_receipt_and_cli(tmp_path, monkeypatch):
    import zipfile
    from scripts import evidence_deficit_replay as module

    fixture_path = Path('contracts/examples/semantic-reconciliation-synthetic-v1.json')
    artifact = tmp_path / 'receipt.zip'
    output = tmp_path / 'out.json'
    report = dict(fixture_bytes_sha256=module.FIXTURE_SHA,
                  relation_orientation='legacy-B-relative-to-A', records=records(fixture()))

    def write_report():
        with zipfile.ZipFile(artifact, 'w') as archive:
            archive.writestr('report.json', json.dumps(report))
        monkeypatch.setattr(module, 'ARTIFACT_SHA', hashlib.sha256(artifact.read_bytes()).hexdigest())

    write_report()
    monkeypatch.setattr('sys.argv', ['deficit-replay', '--fixture', str(fixture_path), '--artifact', str(artifact), '--output', str(output)])
    module.main()
    result = json.loads(output.read_text())
    assert result['fixture_sha256'] == module.FIXTURE_SHA
    assert result['arms']['deficit_minilm']['semantic_calls'] == 4
    bad = tmp_path / 'bad.json'
    bad.write_text('{}')
    with pytest.raises(ValueError, match='fixture hash'):
        module.load(bad, artifact)
    with artifact.open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(ValueError, match='artifact hash'):
        module.load(fixture_path, artifact)
    report['relation_orientation'] = 'unknown'
    write_report()
    with pytest.raises(ValueError, match='protocol mismatch'):
        module.load(fixture_path, artifact)


def test_invalid_prediction_and_ineligible_budget_fail_closed():
    cases = fixture()
    rows = records(cases)
    rows[0]['predictions']['minilm'] = 'unknown'
    with pytest.raises(ValueError, match='invalid cached'):
        bind_predictions(cases, rows)
    cache = bind_predictions(cases, records(cases))
    cache = {key: ('mismatched hash', value[1]) for key, value in cache.items()}
    with pytest.raises(ValueError, match='insufficient matched-budget'):
        replay(cases, cache)


def test_complete_parent_text_available_without_hidden_candidate():
    row = {'id': 'case', 'evidence': {'case:parent': 'exact observed parent'}}
    assert visible_candidate(row) == 'exact observed parent'


def test_formal_controls_retain_false_equivalence_counterexamples():
    from scripts.evidence_deficit_replay import formal_controls

    result = formal_controls()
    assert len(result) == 4
    assert sum(r['reference'] != 'equivalent' and r['lexical'] == 'equivalent' for r in result) == 3
    assert any(r['reference'] == 'equivalent' and r['lexical'] == 'equivalent' for r in result)
