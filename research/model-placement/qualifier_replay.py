"""Replay exact E10 spans from a verified historical artifact; no new inference."""
import argparse
import hashlib
import json
import resource
import time
import zipfile
from collections import Counter
from pathlib import Path

PIN = '5ad26ba90e3aefb2d2fbc28011f73762723acf7774c9dff1cbb7bfe4aa7a57fb'
KINDS = ('applicability', 'condition', 'exception')


def validate(text, spans):
    for kind, start, end in spans:
        if kind not in KINDS or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError('invalid source span')


def complete(text, model, rule, *, guarded=False):
    """Complete only to a unique enclosing same-type rule span; never use references."""
    validate(text, model)
    validate(text, rule)
    out = []
    for kind, start, end in model:
        candidates = {(k, a, b) for k, a, b in rule if k == kind and a <= start < end <= b}
        if len(candidates) == 1:
            out.append(next(iter(candidates)))
        elif not guarded:
            out.append((kind, start, end))
    return out


def overlap_match(gold, pred):
    """Maximum one-to-one typed positive-character overlap, not exact credit."""
    edges = [[j for j, (k, a, b) in enumerate(gold) if k == kind and max(a, start) < min(b, end)] for kind, start, end in pred]
    owner = {}
    def assign(i, seen):
        for j in edges[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in owner or assign(owner[j], seen):
                owner[j] = i
                return True
        return False
    return sum(assign(i, set()) for i in range(len(pred)))


def metrics(gold, pred, *, overlap=False):
    tp = overlap_match(gold, pred) if overlap else sum((Counter(gold) & Counter(pred)).values())
    fp, fn = len(pred) - tp, len(gold) - tp
    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None, 'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}


def summarize(rows, name, *, kind=None, overlap=False):
    # Match within each case. Never let coincident offsets in other cases count.
    tally = Counter()
    for row in rows:
        g = [s for s in row['gold'] if kind is None or s[0] == kind]
        p = [s for s in row['arms'][name] if kind is None or s[0] == kind]
        m = metrics(g, p, overlap=overlap)
        tally.update({k: m[k] for k in ('tp', 'fp', 'fn')})
    tp, fp, fn = (tally[k] for k in ('tp', 'fp', 'fn'))
    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': tp/(tp+fp) if tp+fp else None,
            'recall': tp/(tp+fn) if tp+fn else None, 'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}


def run(path):
    start = time.perf_counter()
    if hashlib.sha256(path.read_bytes()).hexdigest() != PIN:
        raise ValueError('artifact digest mismatch')
    with zipfile.ZipFile(path) as z:
        rule, gliner = [json.loads(z.read(n)) for n in ('rules.json', 'gliner.json')]
    if rule['fixture_sha256'] != gliner['fixture_sha256'] or rule['revision'] != gliner['revision'] or len(rule['cases']) != len(gliner['cases']):
        raise ValueError('unpaired artifacts')
    rows = []
    for a, b in zip(rule['cases'], gliner['cases'], strict=True):
        if any(a[k] != b[k] for k in ('id', 'family', 'text', 'expected')):
            raise ValueError('case mismatch')
        text = a['text']
        gold, rules, model = [[tuple(s) for s in x] for x in (a['expected'], a['predicted'], b['predicted'])]
        for spans in (gold, rules, model):
            validate(text, spans)
        completed = complete(text, model, rules)
        guarded = complete(text, model, rules, guarded=True)
        rows.append({'id': a['id'], 'family': a['family'], 'gold': gold,
                     'arms': {'rules': rules, 'gliner': model, 'completed': completed, 'guarded': guarded,
                              'rule_union_raw': sorted(set(rules) | set(model)),
                              'rule_union_completed': sorted(set(rules) | set(completed))}})
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate cases')
    names = tuple(rows[0]['arms'])
    def group(rs):
        return {name: {'exact': summarize(rs, name), 'overlap': summarize(rs, name, overlap=True),
                       'by_kind': {k: summarize(rs, name, kind=k) for k in KINDS},
                       'empty_outputs': sum(not r['arms'][name] for r in rs),
                       'gained_spans_vs_rules': sum(len((Counter(r['gold']) & Counter(r['arms'][name])) - (Counter(r['gold']) & Counter(r['arms']['rules']))) for r in rs),
                       'lost_spans_vs_rules': sum(len((Counter(r['gold']) & Counter(r['arms']['rules'])) - (Counter(r['gold']) & Counter(r['arms'][name]))) for r in rs)} for name in names}
    return {'protocol': 'e10-operator-completion-replay-v1', 'scientific_qualification': False,
            'canonical_packs_promoted': 0, 'fresh_inference': False, 'new_model_download_bytes': 0,
            'artifact_sha256': PIN, 'source_revision': gliner['revision'], 'fixture_sha256': gliner['fixture_sha256'],
            'summary': group(rows), 'by_family': {f: group([r for r in rows if r['family']==f]) for f in sorted({r['family'] for r in rows})},
            'records': rows, 'wall_seconds': time.perf_counter()-start,
            'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'boundary': 'Retrospective exposed author-labelled synthetic cases; overlap is not correct qualifier interpretation.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.write_text(json.dumps(run(a.artifact), indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')
