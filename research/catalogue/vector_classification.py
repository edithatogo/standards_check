"""Exploratory catalogue classification: fixed-budget vector factorial, not applicability."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import zipfile
from collections import Counter
from itertools import product
from pathlib import Path

ARCHIVE_SHA = '21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01'
FACETS = ('study_types', 'clinical_areas', 'report_sections')
UNKNOWN = {'No study design specified', 'No clinical specialty specified', 'No report section specified', 'Other'}


def design():
    return list(product(('word', 'char'), ('binary', 'count', 'tfidf'), ('full', 'lsa32')))


def groups(rows):
    """Conservative observed identity proxy, not a qualified family-component lock."""
    parent = list(range(len(rows)))
    seen = {}

    def root(i):
        while i != parent[i]:
            i = parent[i]
        return i

    for i, row in enumerate(rows):
        keys = [(k, str(row[k]).strip().casefold()) for k in ('doi', 'pmid') if row.get(k)]
        title = re.sub(r'\W+', ' ', row.get('title', '').casefold()).strip()
        acronym = re.match(r'[a-z][a-z0-9]{2,}', (row.get('acronym') or '').casefold())
        if title:
            keys.append(('title', title))
        if acronym:
            keys.append(('acronym_stem', acronym[0]))
        for key in keys:
            if key in seen:
                parent[root(i)] = root(seen[key])
            else:
                seen[key] = i
    return [rows[root(i)]['id'] for i in range(len(rows))]


def evaluate(rows):
    eligible = [r for r in rows if r['gold']]
    totals = Counter(label for row in eligible for label in row['gold'])
    hits = Counter(label for row in eligible for label in set(row['gold']) & set(row['ranking'][:3]))
    n = len(eligible)
    out = {'eligible': n, 'unknown': len(rows)-n, 'positives': sum(totals.values()),
           'hits_at_3': sum(hits.values()), 'no_rank': sum(not r['ranking'] for r in eligible),
           'per_label': {k: {'positives': v, 'hits_at_3': hits[k]} for k, v in sorted(totals.items())}}
    for k in (1, 3, 5):
        h = [len(set(r['gold']) & set(r['ranking'][:k])) for r in eligible]
        out[f'macro_recall_at_{k}'] = sum(v/len(r['gold']) for v, r in zip(h, eligible, strict=True))/n if n else None
        out[f'micro_recall_at_{k}'] = sum(h)/sum(totals.values()) if totals else None
        out[f'precision_at_{k}'] = sum(h)/(k*n) if n else None
    return out


def labels(row, facet):
    return sorted(set(row.get(facet) or []) - UNKNOWN)


def facet_associations(rows):
    panels = []
    for left, right in ((FACETS[0], FACETS[1]), (FACETS[0], FACETS[2]), (FACETS[1], FACETS[2])):
        eligible = [(labels(r, left), labels(r, right)) for r in rows if labels(r, left) and labels(r, right)]
        a = Counter(x for xs, _ in eligible for x in xs)
        b = Counter(y for _, ys in eligible for y in ys)
        pairs = Counter((x, y) for xs, ys in eligible for x in xs for y in ys)
        panels.append({'left': left, 'right': right, 'eligible': len(eligible),
                       'missing_either': len(rows)-len(eligible),
                       'edges': [{'left': x, 'right': y, 'count': n,
                                  'left_count': a[x], 'right_count': b[y],
                                  'p_right_given_left': n/a[x], 'p_left_given_right': n/b[y],
                                  'jaccard': n/(a[x]+b[y]-n)} for (x,y),n in sorted(pairs.items())]})
    return panels


def rank_scores(scores):
    return [key for key, value in sorted(scores.items(), key=lambda pair: (-pair[1], pair[0])) if value > 0]


def run(catalogue):
    # Optional research stack only; no runtime dependency or new model download.
    import numpy as np
    import sklearn
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
    from sklearn.model_selection import GroupKFold
    from sklearn.preprocessing import normalize

    rows = sorted(catalogue['guidelines'], key=lambda r: r['id'])
    if len(rows) != catalogue['published_count'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('catalogue identities not conserved')
    valid = [r for r in rows if r.get('title')]
    cluster = groups(valid)
    splits = list(GroupKFold(n_splits=5).split(valid, groups=cluster))
    # The same training-fold label prevalence is a no-text comparator at equal K.
    prevalence = {f: {} for f in FACETS}
    for train, test in splits:
        for f in FACETS:
            scores = Counter(label for i in train for label in labels(valid[i], f))
            ranking = rank_scores(scores)[:5]
            for i in test:
                prevalence[f][valid[i]['id']] = ranking
    baseline = {}
    for f in FACETS:
        detail = [{'id': r['id'], 'gold': labels(r, f), 'ranking': prevalence[f].get(r['id'], [])} for r in rows]
        baseline[f] = {'metrics': evaluate(detail), 'rows': detail}
    arms = {}
    for analyzer, weight, reduction in design():
        started = time.perf_counter()
        name = '/'.join((analyzer, weight, reduction))
        observations = {f: {} for f in FACETS}
        dimensions = []
        for train, test in splits:
            vectorizer = CountVectorizer(analyzer=analyzer, ngram_range=(1, 2) if analyzer == 'word' else (3, 5),
                                         binary=weight == 'binary', min_df=1)
            a = vectorizer.fit_transform([valid[i]['title'] for i in train])
            b = vectorizer.transform([valid[i]['title'] for i in test])
            if weight == 'tfidf':
                tfidf = TfidfTransformer().fit(a)
                a, b = tfidf.transform(a), tfidf.transform(b)
            if reduction == 'lsa32':
                reducer = TruncatedSVD(n_components=32, random_state=17).fit(a)
                a, b = reducer.transform(a), reducer.transform(b)
            dimensions.append(a.shape[1])
            scores = normalize(b) @ normalize(a).T
            if hasattr(scores, 'toarray'):
                scores = scores.toarray()
            for pos, i in enumerate(test):
                # Stable tie-break on sorted catalogue IDs; no reference labels at test time.
                nearest = sorted(range(len(train)), key=lambda j: (-scores[pos,j], valid[train[j]]['id']))[:5]
                for f in FACETS:
                    votes = Counter()
                    for j in nearest:
                        if scores[pos,j] > 0:
                            for label in labels(valid[train[j]], f):
                                votes[label] += float(scores[pos,j])
                    observations[f][valid[i]['id']] = rank_scores(votes)[:5]
        arms[name] = {'seconds': time.perf_counter()-started, 'dimensions_by_fold': dimensions, 'facets': {}}
        for f in FACETS:
            details = [{'id': r['id'], 'gold': labels(r,f), 'ranking': observations[f].get(r['id'], [])} for r in rows]
            arms[name]['facets'][f] = {'metrics': evaluate(details), 'rows': details}
    return {'source_revision': catalogue['source_revision'], 'directory_entries': len(rows),
            'title_eligible': len(valid), 'identity_proxy_groups': len(set(cluster)), 'facet_associations': facet_associations(rows),
            'folds': [{'test_ids': [valid[i]['id'] for i in test], 'test_groups': sorted({cluster[i] for i in test})} for _,test in splits],
            'design': [list(row) for row in design()], 'prevalence_baseline': baseline, 'arms': arms,
            'runtime': {'numpy': np.__version__, 'scikit_learn': sklearn.__version__},
            'boundary': 'Catalogue-label recovery with identity proxy grouping; no independent family or semantic validation, no category promotion. Unknown markers excluded as positives.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.artifact.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA:
        raise ValueError('historical catalogue archive digest mismatch')
    with zipfile.ZipFile(args.artifact) as archive:
        report = run(json.loads(archive.read('equator-catalogue.json')))
    report['archive_sha256'] = ARCHIVE_SHA
    report['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
