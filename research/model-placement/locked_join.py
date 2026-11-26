"""Coordinator-only join of locked reference IDs and existing stage receipts.

Checks mechanical consistency; cannot certify scientific independence, rights or
blind adjudication. Never supply this post-inference join to a model runner.
"""
import argparse
import json
from pathlib import Path

from recall_audit import STAGES, STATES, first_failure, stage_counts
from recall_handoff import case_id, digest

OWNERS = {'layout': {'source_anchor'}, 'coordinator': {'candidate_generation', 'rank_cutoff'},
          'offline': {'evidence'}, 'orthogonal': {'decision'}}
TIERS = {'independently_adjudicated', 'model_relative', 'editorial_positive_only',
         'synthetic_author_labelled'}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def join_locked(lock, expected_digest, packets):
    """Join one owner-supplied positive ledger, by reference-bound opaque IDs.

    The caller verifies the actual source/rights/independent-adjudication receipts.
    A pass on this join is not a scientific acceptance or a deployment decision.
    """
    if not sha(expected_digest) or digest(lock) != expected_digest:
        raise ValueError('reference lock digest mismatch')
    tier = lock['reference_tier']
    if tier not in TIERS or not nonempty(lock['reference_ledger_receipt']) or not sha(lock['eligible_universe_digest']):
        raise ValueError('reference metadata incomplete')
    if tier == 'independently_adjudicated':
        qualification = lock.get('qualification_receipts', {})
        if not all(nonempty(qualification.get(k)) for k in ('source_rights', 'anchor_fidelity', 'blinded_initial_labels', 'independent_resolution', 'family_partition', 'complete_pool_reference')):
            raise ValueError('independent qualification receipts incomplete')
    arms = lock['arms']
    if not arms or not all(nonempty(a) for a in arms) or len(arms) != len(set(arms)) or not lock['cases']:
        raise ValueError('empty or duplicate arm/reference denominator')
    indexed, family_splits = {}, {}
    for c in lock['cases']:
        if not all(nonempty(c.get(k)) for k in ('namespace', 'family_component', 'split', 'source_anchor', 'target_anchor')):
            raise ValueError('case identity or anchor missing')
        family, split = c['family_component'], c['split']
        if split not in ('development', 'calibration', 'evaluation') or family_splits.setdefault(family, split) != split:
            raise ValueError('family component crosses partitions')
        pool, review = c['candidate_budget'], c['review_budget']
        if type(pool) is not int or type(review) is not int or not 0 < review <= pool:
            raise ValueError('invalid candidate/review budget')
        required = c.get('required_components', [])
        if not all(nonempty(x) for x in required) or len(set(required)) != len(required):
            raise ValueError('invalid required bundle components')
        ident = case_id(c['namespace'], expected_digest, c['original_id'])
        if ident in indexed:
            raise ValueError('duplicate locked case')
        indexed[ident] = c
    merged = {(ident, arm): {'case_id': ident, 'namespace': c['namespace'], 'reference_tier': tier,
              'reference_digest': expected_digest, 'original_id': c['original_id'], 'arm': arm,
              'family_component': c['family_component'], 'split': c['split'], 'source_anchor': c['source_anchor'],
              'target_anchor': c['target_anchor'], 'candidate_budget': c['candidate_budget'],
              'review_budget': c['review_budget'], 'required_components': c.get('required_components', []),
              'stages': dict.fromkeys(STAGES, 'unknown'), 'stage_receipts': {}}
              for ident, c in indexed.items() for arm in arms}
    for packet in packets:
        if packet['reference_lock_digest'] != expected_digest:
            raise ValueError('stage packet lock mismatch')
        owner = packet['owner']
        if owner not in OWNERS:
            raise ValueError('unknown stage owner')
        for obs in packet['rows']:
            key = (obs['case_id'], obs['arm'])
            if key not in merged:
                raise ValueError('case or arm outside locked denominator')
            target = merged[key]
            stages = obs['stages']
            if not stages or not set(stages) <= OWNERS[owner] or not set(stages.values()) <= STATES:
                raise ValueError('stage owner or state mismatch')
            if not nonempty(obs.get('receipt')):
                raise ValueError('missing stage receipt')
            for stage, state in stages.items():
                previous = target['stage_receipts'].get(stage)
                record = {'owner': owner, 'receipt': obs['receipt'], 'state': state}
                if previous is not None and previous != record:
                    raise ValueError('conflict between stage receipts')
                target['stages'][stage] = state
                target['stage_receipts'][stage] = record
            if owner == 'coordinator':
                for name, stage, cutoff in (('candidate_rank', 'candidate_generation', target['candidate_budget']),
                                            ('review_rank', 'rank_cutoff', target['review_budget'])):
                    if name not in obs:
                        continue
                    rank = obs[name]
                    if rank is not None and (type(rank) is not int or not 0 < rank <= target['candidate_budget']):
                        raise ValueError('rank outside candidate budget')
                    state = stages.get(stage, 'unknown')
                    if state == 'pass' and (rank is None or rank > cutoff) or state == 'fail' and rank is not None and rank <= cutoff:
                        raise ValueError('rank conflicts with stage state')
                    if name in target and target[name] != rank:
                        raise ValueError('conflicting rank receipts')
                    target[name] = rank
            if 'decision' in stages:
                detail = obs.get('decision_detail')
                if stages['decision'] == 'pass':
                    if detail not in ('accepted', 'referral_resolved'):
                        raise ValueError('pass requires accepted or actual resolution')
                    if detail == 'referral_resolved' and not nonempty(obs.get('resolution_receipt')):
                        raise ValueError('review resolution requires actual receipt')
                    covered = obs.get('covered_components', [])
                    if not set(target['required_components']) <= set(covered):
                        raise ValueError('incomplete required bundle')
                target['decision_detail'] = detail
                target['covered_components'] = obs.get('covered_components', [])
                target['resolution_receipt'] = obs.get('resolution_receipt')
    rows = list(merged.values())
    for r in rows:
        for i, s in enumerate(STAGES):
            if r['stages'][s] == 'not_reached' and not any(r['stages'][p] == 'fail' for p in STAGES[:i]):
                raise ValueError('not_reached without an observed upstream exclusion')
        r['first_observed'], r['first_established'] = first_failure(r['stages'])
    summary = {a: {s: stage_counts([r for r in rows if r['arm'] == a and r['split'] == s])
                   for s in sorted(set(family_splits.values()))} for a in arms}
    return {'protocol': 'shared-missed-match-development-v1', 'reference_lock_digest': expected_digest,
            'reference_tier': tier, 'eligible_universe_digest': lock['eligible_universe_digest'],
            'reference_ledger_receipt': lock['reference_ledger_receipt'],
            'independent_positive_count': len(indexed) if tier == 'independently_adjudicated' else 0,
            'scientific_qualification': False, 'semantic_merges': 0, 'rows': rows, 'summary': summary,
            'boundary': 'Mechanical join only; supplied reference provenance requires external verification.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference-lock', type=Path, required=True)
    p.add_argument('--reference-digest', required=True)
    p.add_argument('--stage-receipt', type=Path, action='append', default=[])
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = join_locked(json.loads(a.reference_lock.read_bytes()), a.reference_digest,
                         [json.loads(path.read_bytes()) for path in a.stage_receipt])
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')
