import copy
from collections import Counter
from pathlib import Path

import pytest

from scripts.equator_resume_batch import resume


def initial():
    rows = []
    work = []
    for i, status in enumerate(("held", "deferred_acquisition_budget", "source_inventory_observed_not_reconciled", "deferred_acquisition_budget"), 1):
        key = f"equator:{i}"
        ident = f"PMC{i}"
        rows.append({"id": key, "source_blob_sha": "a" * 40})
        work.append({"pmcid": ident, "source_ids": [key], "identity_pairs": [[f"10.1000/{i}", str(i)]], "status": "candidate_pending_acquisition"})
    bulk = [{"edition": "candidate:" + w["pmcid"], "pmcid": w["pmcid"], "doi": w["identity_pairs"][0][0], "pmid": w["identity_pairs"][0][1], "source_blobs": [[w["source_ids"][0], "a" * 40]], "status": status, "canonical_packs_promoted": 0, **({"source_sha256": "b" * 64, "table_inventory": []} if status == "source_inventory_observed_not_reconciled" else {})} for w, status in zip(work, ("held", "deferred_acquisition_budget", "source_inventory_observed_not_reconciled", "deferred_acquisition_budget"), strict=True)]
    return {"schema_version": 1, "source_revision": "c" * 40, "records": rows, "oa_source_worklist": work, "bulk_articles": bulk, "summary": {"bulk_status_counts": dict(Counter(r["status"] for r in bulk))}}


def test_resume_retains_held_and_successful_rows_and_passes_only_pending_first():
    prior = initial()
    seen = []
    def survey(report, history, root, limit):
        seen.append((copy.deepcopy(report), copy.deepcopy(history), limit))
        return [{**r, "status": "held", "acquisition_origin": "current_observation"} if r["pmcid"] == "PMC2" else {**r, "status": "deferred_acquisition_budget"} for r in report["bulk_articles"] if r["pmcid"] in {w["pmcid"] for w in report["oa_source_worklist"]}]
    result = resume(prior, Path('.'), 1, survey)
    assert len(result['bulk_articles']) == 4
    assert [w['pmcid'] for w in seen[0][0]['oa_source_worklist']] == ['PMC2']
    assert result['bulk_articles'][0]['status'] == 'held'
    assert result['bulk_articles'][2]['status'] == 'source_inventory_observed_not_reconciled'
    assert result['resume']['attempted'] == ['PMC2']
    assert result['resume']['remaining_unattempted'] == 1
    assert prior['bulk_articles'][1]['status'] == 'deferred_acquisition_budget'
    next_result = resume(result, Path('.'), 1, survey)
    assert [w['pmcid'] for w in seen[1][0]['oa_source_worklist']] == ['PMC4']
    assert next_result['bulk_articles'][1]['status'] == 'held'


def test_reject_nonconserving_and_changed_identity():
    prior = initial()
    with pytest.raises(ValueError, match='budget'):
        resume(prior, Path('.'), 25, lambda *a: [])
    with pytest.raises(ValueError, match='inventory'):
        resume(prior, Path('.'), 1, lambda *a: [])
    prior['bulk_articles'][1]['source_blobs'] = [['equator:2', 'wrong']]
    with pytest.raises(ValueError, match='binding'):
        resume(prior, Path('.'), 1, lambda *a: [])


def test_explicit_retry_does_not_replay_success():
    prior = initial()
    for row in prior['bulk_articles']:
        if row['status'] == 'deferred_acquisition_budget':
            row['status'] = 'held'
    result = resume(prior, Path('.'), 2, lambda report, history, root, limit: [{**r, 'status': 'held', 'acquisition_origin': 'current_observation'} for r in report['bulk_articles'] if r['pmcid'] in {w['pmcid'] for w in report['oa_source_worklist']}])
    assert result['resume']['attempted'] == []
    result = resume(prior, Path('.'), 2, lambda report, history, root, limit: [{**r, 'status': 'held', 'acquisition_origin': 'current_observation'} for r in report['bulk_articles'] if r['pmcid'] in {w['pmcid'] for w in report['oa_source_worklist']}], retry_held=True)
    assert result['resume']['attempted'] == ['PMC1', 'PMC2']
