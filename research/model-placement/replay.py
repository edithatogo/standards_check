"""Opt-in, offline replay of hash-bound historical development receipts.
No fresh neural inference, no independent reference or semantic admission.
"""
import argparse
import hashlib
import json
import math
import resource
import time
import zipfile
from collections import defaultdict
from pathlib import Path

PINS = {
    15087556116: 'd796bdbc6a84830a7e3c702fbc6d08ce9fe9430175db5a4610b0ad0dfa2c2ae9',
    15091873096: 'd514f12e0a53e1c5749f23d68eb9fb5a6c6ef2ee8155428bac8cd71c445e48e6',
    15088716936: '3df9b23127cf07cc67c55ccd18ce942895d70a62769015699cd2af1c95cdb20e',
    15091588651: '9b083ef4c1f294fc60e3694de2b308893dc704d9045b6d132d5cf99fd3671abe',
}


def load(root, ident, member):
    path = root / f'github-actions-artifact-{ident}.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINS[ident]:
        raise ValueError('artifact hash mismatch')
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(member))


def fuse(*orders):
    scores = defaultdict(float)
    for order in orders:
        if len(set(order)) != len(order):
            raise ValueError('duplicate ranking')
        for i, key in enumerate(order, 1):
            scores[key] += 1 / (60 + i)
    return sorted(scores, key=lambda key: (-scores[key], key))


def select(ids, priority, n):
    if not 0 <= n <= len(ids) or len(set(ids)) != len(ids):
        raise ValueError('invalid budget')
    return set(sorted(ids, key=lambda key: (-priority(key), key))[:n])


def choose(first, second):
    if first == 'abstain':
        return second
    if second == 'abstain' or first == second:
        return first
    return 'abstain'


def decision_metrics(ref, predicted, baseline=None):
    if set(ref) != set(predicted) or baseline is not None and set(ref) != set(baseline):
        raise ValueError('paired coverage mismatch')
    out = {'n': len(ref), 'correct': sum(ref[k] == predicted[k] for k in ref),
           'abstained': sum(predicted[k] == 'abstain' for k in ref),
           'false_equivalence': sum(predicted[k] == 'equivalent' and ref[k] != 'equivalent' for k in ref)}
    out['coverage'] = (out['n'] - out['abstained']) / out['n']
    if baseline is not None:
        out['gain'] = sum(predicted[k] == ref[k] and baseline[k] != ref[k] for k in ref)
        out['loss'] = sum(predicted[k] != ref[k] and baseline[k] == ref[k] for k in ref)
    return out


def entropy(p):
    return -sum(v * math.log(v) for v in p.values() if v > 0)


def decisions(root):
    historical = load(root, 15087556116, 'report.json')
    framing = load(root, 15091873096, 'report.json')
    h = {r['id']: r for r in historical['records']}
    f = {r['id']: r for r in framing['records']}
    if set(h) != set(f) or historical['fixture_bytes_sha256'] != framing['fixture_bytes_sha256']:
        raise ValueError('fixture mismatch')
    out = {}
    all_predictions = {}
    for family in sorted({r['family'] for r in h.values()}):
        ids = sorted(k for k, r in h.items() if r['family'] == family)
        ref = {k: h[k]['reference'] for k in ids}
        view = lambda k: f[k]['views']['original']
        base = {k: view(k)['prediction'] for k in ids}
        pred = {'minilm': {k: h[k]['predictions']['minilm'] for k in ids},
                'deberta': {k: h[k]['predictions']['deberta'] for k in ids},
                'direct': base,
                'directional': {k: view(k)['directional'] for k in ids},
                'witness': {k: f[k]['views']['witness']['prediction'] for k in ids},
                'four_view_agreement': {k: f[k]['agreement'] for k in ids}}
        # Same three additional swapped-view requests per six-case family.
        # Difficulty: entropy of three directional questions. Uncertainty/disagreement:
        # direct/directional mismatch first, then direct relation entropy. No labels used.
        priorities = {'fixed': lambda k: 0,
                      'difficulty': lambda k: sum(entropy(view(k)['probabilities'][q]) for q in ('a_to_b', 'b_to_a', 'joint')),
                      'uncertain_disagree': lambda k: 10 * (view(k)['prediction'] != view(k)['directional']) + entropy(view(k)['probabilities']['relation'])}
        selected = {}
        for name, priority in priorities.items():
            chosen = select(ids, priority, len(ids) // 2)
            selected[name] = sorted(chosen)
            pred['route_' + name] = {k: choose(base[k], f[k]['views']['swapped']['prediction']) if k in chosen else base[k] for k in ids}
        out[family] = {'split': h[ids[0]]['split'], 'metrics': {a: decision_metrics(ref, p, base) for a, p in pred.items()}, 'selected': selected}
        all_predictions.update({k: {'family': family, 'split': h[k]['split'], 'reference': ref[k], 'predictions': {a: p[k] for a, p in pred.items()}} for k in ids})
    summary = {}
    for split in ('dev', 'test'):
        rows = {k: r for k, r in all_predictions.items() if r['split'] == split}
        ref = {k: r['reference'] for k, r in rows.items()}
        base = {k: r['predictions']['direct'] for k, r in rows.items()}
        summary[split] = {a: decision_metrics(ref, {k: r['predictions'][a] for k, r in rows.items()}, base) for a in next(iter(rows.values()))['predictions']}
    return {'by_family': out, 'summary': summary, 'records': all_predictions, 'budget': 'one original and half a swapped request per case; replay request-count proxy, not equal wall/compute'}


def retrieval(root):
    baseline = load(root, 15088716936, 'paired.json')['results']
    qwen = load(root, 15091588651, 'report.json')
    key = lambda r: (r['instrument_id'], r['item_id'])
    bge = {key(r): r['ranking'] for r in baseline['bge']['rows']}
    char = {key(r): r['ranking'] for r in baseline['char']['rows']}
    ref = {key(r): set(r['reference']) for r in baseline['bge']['rows']}
    scores = {key(r): r['scores'] for r in qwen['provider_rows']}
    neural = {key(r): r['ranking'] for r in qwen['result']['rows']}
    minilm = {key(r): r['ranking'] for r in baseline['bge_then_reranker10']['rows']}
    if not (set(bge) == set(char) == set(ref) == set(scores) == set(neural) == set(minilm)) or any(set(scores[k]) != set(bge[k][:10]) for k in bge):
        raise ValueError('receipt pool mismatch')
    fused = {k: fuse(bge[k], char[k]) for k in bge}
    # Classical lexical reranking fallback: no invented neural scores for new pool members.
    def lexical(pool, order):
        index = {v: i for i, v in enumerate(order)}
        return sorted(pool, key=lambda v: (index.get(v, len(order)), v))
    ranked = {'bge': {k: bge[k][:10] for k in bge}, 'fused': {k: fused[k][:10] for k in bge},
              'minilm_original': minilm, 'qwen_original': neural,
              'lexical_original': {k: lexical(bge[k][:10], char[k]) for k in bge},
              'lexical_fused': {k: lexical(fused[k][:10], char[k]) for k in bge}}
    for a, pool in [('lexical_original', 'bge'), ('lexical_fused', 'fused'), ('qwen_original', 'bge'), ('minilm_original', 'bge')]:
        if any(set(ranked[a][k]) != set(ranked[pool][k]) for k in bge):
            raise ValueError('reranker changed pool')
    # Evidence evaluator replay: low max Qwen score in first five -> another five candidates,
    # at identical per-instrument budgets. Rank scores are relevance, not evidence truth.
    first = {k: bge[k][:5] for k in bge}
    certainty = {k: max(scores[k][v] for v in first[k]) for k in bge}
    ids = sorted(bge)
    fixed, triggered = set(), set()
    for inst in sorted({k[0] for k in ids}):
        group = [k for k in ids if k[0] == inst]
        fixed |= select(group, lambda k: 0, len(group)//2)
        triggered |= select(group, lambda k: -certainty[k], len(group)//2)
    def extend(chosen, ranks):
        return {k: first[k] + [v for v in ranks[k] if v not in first[k]][:5] if k in chosen else first[k] for k in ids}
    ranked.update({'first5': first, 'fixed_second': extend(fixed, fused), 'triggered_second': extend(triggered, fused),
                   'triggered_continue': extend(triggered, bge), 'score_abstain': {k: first[k] if certainty[k] >= .05 else [] for k in ids}})
    def metrics(name, group):
        order = ranked[name]
        comparator = ranked['fused' if name == 'lexical_fused' else 'first5' if name in ('fixed_second','triggered_second','triggered_continue','score_abstain') else 'bge']
        ans = {'queries': len(group), 'associations': sum(len(ref[k]) for k in group), 'candidates': sum(len(order[k]) for k in group), 'abstentions': sum(not order[k] for k in group)}
        for n in (1, 5, 10):
            before = {k: set(comparator[k][:n]) & ref[k] for k in group}
            after = {k: set(order[k][:n]) & ref[k] for k in group}
            ans[str(n)] = {'macro_recall': sum(len(after[k])/len(ref[k]) for k in group)/len(group), 'hits': sum(map(len, after.values())), 'misses': ans['associations']-sum(map(len, after.values())), 'gain': sum(len(after[k]-before[k]) for k in group), 'loss': sum(len(before[k]-after[k]) for k in group)}
        return ans
    return {'summary': {a: metrics(a, ids) for a in ranked}, 'by_instrument': {i: {a: metrics(a, [k for k in ids if k[0] == i]) for a in ranked} for i in sorted({k[0] for k in ids})}, 'records': [{'id': list(k), 'known_associations': sorted(ref[k]), 'first5_max_score': certainty[k], 'rankings': {a: orders[k] for a, orders in ranked.items()}} for k in ids], 'boundary': 'editorial positive associations only; unlisted association is not established negative, unsupported decisions cannot be scored'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    result = {'protocol': 'model-placement-replay-development-v1', 'scientific_qualification': False, 'semantic_merges': 0, 'artifact_pins': PINS, 'decisions': decisions(args.artifacts), 'retrieval': retrieval(args.artifacts), 'fresh_model_download_bytes': 0}
    result['wall_seconds'] = time.perf_counter()-started
    result['peak_rss_kib_linux'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
