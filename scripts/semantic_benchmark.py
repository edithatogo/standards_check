"""Experimental semantic diagnostics; never grant admission or rights."""
from __future__ import annotations
from collections import Counter
import math

LABELS = ('contradiction', 'entailment', 'neutral')
THRESHOLDS = (.5, .6, .7, .8, .9, .95, .99, 1.01)


def validate_cases(cases):
    if not cases or len({row['id'] for row in cases}) != len(cases):
        raise ValueError('empty or duplicate benchmark cases')
    groups = {'dev': set(), 'test': set()}
    for row in cases:
        if (row['split'] not in groups or row['forward'] not in LABELS or row['reverse'] not in LABELS
                or not all(isinstance(row[k], str) and row[k].strip() for k in ('id', 'family', 'source', 'candidate'))):
            raise ValueError('invalid case or direction')
        groups[row['split']].add(row['family'])
    if not all(groups.values()) or groups['dev'] & groups['test']:
        raise ValueError('family-level split required')


def probabilities(values):
    if len(values) != 3 or any(not math.isfinite(v) or not 0 <= v <= 1 for v in values) or not math.isclose(sum(values), 1, abs_tol=1e-5):
        raise ValueError('invalid NLI probabilities')
    return tuple(float(v) for v in values)


def entailment_score(forward, reverse):
    a, b = probabilities(forward), probabilities(reverse)
    return min(a[1], b[1]) if all(p[1] > max(p[0], p[2]) for p in (a, b)) else 0.0


def bidirectional(forward, reverse, threshold):
    if threshold not in THRESHOLDS:
        raise ValueError('unregistered threshold')
    return entailment_score(forward, reverse) >= threshold


def measures(expected, predicted):
    if len(expected) != len(predicted):
        raise ValueError('prediction coverage mismatch')
    c = Counter(zip(expected, predicted))
    return {'n':len(expected),'tp':c[True,True],'fp':c[False,True],
            'tn':c[False,False],'fn':c[True,False],'accepted':sum(predicted)}


def select_threshold(dev):
    if not dev:
        raise ValueError('development split required')
    ranked = []
    for t in THRESHOLDS:
        result = measures([truth for _,truth in dev], [score >= t for score,_ in dev])
        if not result['fp']:
            ranked.append((result['tp'], t))
    return max(ranked)[1]


MODEL_ID = 'cross-encoder/nli-MiniLM2-L6-H768'
MODEL_REVISION = 'c847a3c0e1cad93a5343183ef183f3044e3fc7c2'
MODEL_SHA256 = '44391a5241a62e0083c1a8899a71e69a092b95aea5ba89e14062925468eceac7'


class LocalNLI:
    """Pinned, CPU-only ONNX; local tokenizer and label map; never truncate."""
    def __init__(self, directory):
        import json
        import hashlib
        import onnxruntime as ort
        from tokenizers import Tokenizer
        model = directory / 'model_quint8_avx2.onnx'
        if model.stat().st_size > 100_000_000 or hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA256:
            raise ValueError('unqualified ONNX model bytes')
        config = json.loads((directory / 'config.json').read_text())
        if [config['id2label'][str(i)].lower() for i in range(3)] != list(LABELS):
            raise ValueError('NLI label order differs from pinned contract')
        self.tokenizer = Tokenizer.from_file(str(directory / 'tokenizer.json'))
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(model), sess_options=options, providers=['CPUExecutionProvider'])
        self.inputs = {i.name for i in self.session.get_inputs()}
        if not {'input_ids', 'attention_mask'} <= self.inputs <= {'input_ids', 'attention_mask', 'token_type_ids'}:
            raise ValueError('unsupported model inputs')
        self.version = ort.__version__
        self.asset_hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                             for name in ('model_quint8_avx2.onnx', 'tokenizer.json', 'config.json')}

    def score(self, premise, hypothesis):
        import numpy as np
        e = self.tokenizer.encode(premise, hypothesis)
        if len(e.ids) > 512:
            raise ValueError('pair exceeds context; no silent truncation')
        values = {'input_ids': e.ids, 'attention_mask': e.attention_mask, 'token_type_ids': e.type_ids}
        output = self.session.run(None, {name: np.asarray([values[name]], dtype=np.int64) for name in self.inputs})
        logits = np.asarray(output[0], dtype=np.float64)
        if logits.shape != (1, 3) or not np.isfinite(logits).all():
            raise ValueError('unexpected NLI output')
        exponent = np.exp(logits[0] - logits[0].max())
        return probabilities((exponent / exponent.sum()).tolist())


def dependency_similarity(nlp, source, candidate):
    """Compare typed lemma edges, retaining negation, roles and dependencies."""
    def arcs(text):
        doc = nlp(text)
        if not doc.has_annotation('DEP') or not doc.has_annotation('LEMMA'):
            raise ValueError('dependency and lemma annotations required')
        return Counter((token.lemma_.casefold(), token.pos_, token.dep_, token.head.lemma_.casefold())
                       for token in doc if not token.is_space and not token.is_punct)
    a, b = arcs(source), arcs(candidate)
    total = sum((a | b).values())
    return sum((a & b).values()) / total if total else 0.0


def evaluate(cases, nlp, nli):
    import time
    from .source_reconciliation import linguistic_compare
    validate_cases(cases)
    records = []
    timings = Counter()
    for row in cases:
        source, candidate = row['source'], row['candidate']
        start = time.perf_counter()
        findings = linguistic_compare(source, candidate)
        lexical = findings['similarity_permille'] / 1000
        material = set(findings['findings']) - {'lexical', 'surface', 'punctuation'}
        markers = lexical if not material else 0.0
        timings['lexical_markers'] += time.perf_counter() - start
        start = time.perf_counter()
        dep = dependency_similarity(nlp, source, candidate)
        timings['dependency'] += time.perf_counter() - start
        start = time.perf_counter()
        forward, reverse = nli.score(source, candidate), nli.score(candidate, source)
        timings['nli'] += time.perf_counter() - start
        scores = {'exact': float(findings['exact']), 'lexical': lexical, 'classical': markers,
                  'dependency': dep, 'classical_plus_dependency': (markers + dep) / 2 if not material else 0.0,
                  'bidirectional_nli': entailment_score(forward, reverse)}
        records.append({'id': row['id'], 'family': row['family'], 'split': row['split'],
                        'expected': row['forward'] == row['reverse'] == 'entailment',
                        'expected_directions': [row['forward'], row['reverse']],
                        'scores': scores, 'findings': findings['findings'],
                        'forward_probabilities': forward, 'reverse_probabilities': reverse,
                        'source_sha256': findings['source_sha256'], 'candidate_sha256': findings['candidate_sha256']})
    summary = {}
    dev = [r for r in records if r['split'] == 'dev']
    test = [r for r in records if r['split'] == 'test']
    for name in records[0]['scores']:
        threshold = 1.0 if name == 'exact' else select_threshold([(r['scores'][name], r['expected']) for r in dev])
        summary[name] = {'threshold': threshold}
        for split, group in [('dev', dev), ('test', test)]:
            predicted = [r['scores'][name] >= threshold for r in group]
            summary[name][split] = measures([r['expected'] for r in group], predicted)
        summary[name]['test_by_family'] = {
            f: measures([r['expected'] for r in test if r['family'] == f],
                        [r['scores'][name] >= threshold for r in test if r['family'] == f])
            for f in sorted({r['family'] for r in test})}
        for record in records:
            record.setdefault('candidate_only', {})[name] = record['scores'][name] >= threshold
    confusion = Counter()
    for row in test:
        for direction, expected, p in zip(('forward', 'reverse'), row['expected_directions'],
                                           (row['forward_probabilities'], row['reverse_probabilities'])):
            actual = LABELS[max(range(3), key=lambda i: p[i])]
            confusion[(direction, expected, actual)] += 1
    return {'summary': summary, 'records': records, 'test_directional_confusion': [
        {'direction': d, 'expected': e, 'predicted': p, 'n': n} for (d,e,p), n in sorted(confusion.items())],
        'wall_seconds': dict(timings), 'canonical_packs_promoted': 0,
        'claim_boundary': 'Synthetic analyst-authored labels; diagnostic candidate decisions only; no independent methodological validation.'}


def main():
    import argparse
    import hashlib
    import json
    import platform
    import resource
    from pathlib import Path
    import spacy
    import time
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    raw = args.cases.read_bytes()
    fixture = json.loads(raw)
    if fixture.get('schema_version') != 1 or fixture.get('label_origin') != 'synthetic_analyst_authored':
        raise ValueError('unqualified benchmark fixture')
    start = time.perf_counter()
    nlp = spacy.load('en_core_web_sm')
    if nlp.meta['version'] != '3.8.0':
        raise ValueError('unqualified spaCy pipeline version')
    nli = LocalNLI(args.assets)
    load_seconds = time.perf_counter() - start
    report = evaluate(fixture['cases'], nlp, nli)
    report.update({'schema_version': 1, 'revision': args.revision,
                   'fixture_sha256': hashlib.sha256(raw).hexdigest(), 'label_origin': fixture['label_origin'],
                   'model_id': MODEL_ID, 'model_revision': MODEL_REVISION, 'model_files_sha256': nli.asset_hashes,
                   'onnxruntime_version': nli.version, 'spacy_version': spacy.__version__,
                   'spacy_model': nlp.meta['version'], 'python_version': platform.python_version(),
                   'machine': platform.machine(), 'load_seconds': load_seconds,
                   'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
