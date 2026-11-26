"""Opt-in paired neural reranking; same ten candidates within each comparison."""

import argparse
import json
import math
import resource
import time
from collections import defaultdict
from pathlib import Path


def fixed_pools(bge, char, universe, *, budget=10):
    if not 0 < budget <= len(universe) or not bge or set(bge) != set(char):
        raise ValueError('query coverage or budget mismatch')
    fused = {}
    for key, order in bge.items():
        if len(order) != len(set(order)) or len(char[key]) != len(set(char[key])):
            raise ValueError('duplicate candidates')
        if set(order) != universe or not set(char[key]) <= universe:
            raise ValueError('candidate universe mismatch')
        scores = defaultdict(float)
        for seq in (order, char[key]):
            for i, candidate in enumerate(seq, 1):
                scores[candidate] += 1 / (60 + i)
        fused[key] = sorted(scores, key=lambda c: (-scores[c], c))[:budget]
    return {'bge': {key: order[:budget] for key, order in bge.items()}, 'fused': fused}


def score_pool(queries, targets, pools, scorer, *, budget=10):
    if set(pools) != set(queries) or not queries:
        raise ValueError('query coverage mismatch')
    if any(len(p) != budget or len(set(p)) != budget or not set(p) <= set(targets) for p in pools.values()):
        raise ValueError('invalid fixed candidate pool')
    ranked, rows = {}, []
    for key, pool in sorted(pools.items()):
        scores = {}
        for candidate in pool:
            value = scorer(queries[key], targets[candidate])
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError('nonfinite or invalid score')
            scores[candidate] = value
        ranked[key] = sorted(pool, key=lambda c: (-scores[c], c))
        rows.append({'instrument_id': key[0], 'item_id': key[1], 'pool': pool, 'scores': scores})
    return ranked, rows


def run(root, baseline, assets, pool_name):
    from scripts import costing_retrieval as cost

    _, _, queries, targets, references, paths = cost.load_inputs(root)
    pins = {p.name: cost.file_hash(p) for p in paths}
    if pins != cost.FROZEN_INPUT_SHA256:
        raise ValueError('frozen costing inputs changed')
    prior = json.loads(baseline.read_text(encoding='utf-8'))
    if prior['input_sha256'] != pins or prior['scientific_qualification'] or prior['semantic_merges']:
        raise ValueError('invalid baseline receipt')
    def extract(name):
        rows = prior['results'][name]['rows']
        order = {(r['instrument_id'], r['item_id']): r['ranking'] for r in rows}
        if len(order) != len(rows) or set(order) != set(queries):
            raise ValueError('baseline query mismatch')
        if any(set(r['reference']) != references[r['instrument_id'], r['item_id']] for r in rows):
            raise ValueError('baseline reference mismatch')
        return order
    bge, char = extract('bge'), extract('char')
    if cost.pool_sha256(bge, 10) != cost.FROZEN_POOL_SHA256:
        raise ValueError('frozen BGE shortlist changed')
    if char != cost.lexical_rankings(queries, targets, 'char'):
        raise ValueError('lexical rankings drifted')
    if prior['models']['bge']['sha256'] != cost.MODELS['bge']['sha256']:
        raise ValueError('BGE model pin mismatch')
    pools = fixed_pools(bge, char, set(targets))
    if pool_name not in pools:
        raise ValueError('unknown pool')
    selected = pools[pool_name]
    started = time.perf_counter()
    ranker = cost.LocalRanker(assets / 'reranker', 'reranker')
    load_seconds = time.perf_counter() - started
    started = time.perf_counter()
    ranked, rows = score_pool(queries, targets, selected, ranker)
    scoring_seconds = time.perf_counter() - started
    result = cost.evaluate(references, set(targets), ranked)
    return {
        'protocol': 'fixed-pool-reranker-development-v1',
        'pool': pool_name,
        'input_sha256': pins,
        'baseline_sha256': cost.file_hash(baseline),
        'pool_sha256': cost.pool_sha256(selected, 10),
        'pool_incumbent': cost.evaluate(references, set(targets), selected),
        'result': result,
        'paired': cost.paired_retrieval(references, selected, ranked),
        'scores': rows,
        'score_calls': sum(len(r['pool']) for r in rows),
        'model': {**cost.MODELS['reranker'], 'assets': ranker.asset_hashes, 'runtime_version': ranker.version},
        'model_weight_bytes': (assets / 'reranker' / 'model.onnx').stat().st_size,
        'asset_bytes': {p.name: p.stat().st_size for p in (assets / 'reranker').iterdir() if p.is_file()},
        'load_seconds': load_seconds,
        'scoring_seconds': scoring_seconds,
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'reference_status': 'research_seed_review_required',
        'scientific_qualification': False,
        'semantic_merges': 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--pool', choices=('bge', 'fused'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        result = run(args.root, args.baseline, args.assets, args.pool)
    except Exception as exc:
        args.output.write_text(json.dumps({'status': 'failed', 'pool': args.pool, 'error_type': type(exc).__name__, 'seconds': time.perf_counter() - started, 'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'scientific_qualification': False, 'semantic_merges': 0}) + '\n', encoding='utf-8')
        raise SystemExit('fixed-pool run failed; sanitized receipt retained') from None
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
