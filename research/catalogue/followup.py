"""Matched catalogue classifier follow-up and conservative title-role candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import zipfile
from collections import Counter
from pathlib import Path

from .ontology_projection import mentions
from .vector_classification import ARCHIVE_SHA, FACETS, evaluate, groups, labels, rank_scores


MEMBER_SHA = 'abea437bf8bc34a14a6022c8e76367cd994e49bc6e888b2943030381068fa868'
TERMS_SHA = 'ffb58e00328993a84e8e59bcf363fa0e36ced636077cc3ec46fb4a1ab1e1029f'
FOLDS_SHA = '60b45222383886986d8b203aec093dd287eaf6d016c59323aac6804c2461cdf3'
PREVIOUS_SHA = 'b0a67a7123478f3283adbf4608e7cdf523875994f6e3cfd0e239f3784a8c8a19'
METHODS = ('knn', 'logistic', 'balanced')
# Exact retained assignments on sorted titled catalogue IDs. Do not recompute tied groups.
FOLD_ASSIGNMENT = (
    '20432104311043210404432124321043010432232104432144321043222104321043210431211104'
    '00043214044443210432104304321043210432100430200000000000010000000200104113442103'
    '32104342121043210432004321104321043210432104321032104321024321043213044003431132'
    '10334321443210432042210432104321043104321043210432104321104321043210423210421043'
    '21043210432104312104341043210432102104321043210432104343210432104322104111111111'
    '11311111124321043210432104333321132104321043210432132221043210432111044321040432'
    '10432104321043042321004321043210432004321043210432104344043210432104321043212104'
    '32103333333333333444213043212104323130432104333333221044102222222222222423210432'
    '1204321041043210432104321040442321404321044444443210432132112222432104033321043'
)


def role(text, start, end):
    """Candidate cues only; no implication from unclassified or negated mentions."""
    if not 0 <= start < end <= len(text):
        raise ValueError('invalid span')
    prefix = re.split(r'[:;.!?]', text[:start].casefold())[-1]
    if re.search(r'\b(?:except|excluding|not|without|rather than|unlike)\b', prefix):
        return 'unresolved'
    if re.search(r'\b(?:developed|development|derived|informed)\s+(?:using|by|through|from|based on)\s+(?:an?\s+)?$', prefix):
        return 'development_candidate'
    if re.search(r'\b(?:reporting|guidelines? for|checklists? for)\s+(?:the\s+|an?\s+|of\s+)*$', prefix):
        return 'target_candidate'
    return 'unresolved'


def role_audit(rows, terms):
    by_concept = {t['id']: t for t in terms}
    counts, novel, held, details = Counter(), set(), set(), []
    for row in rows:
        text = row.get('title') or ''
        declared = set(labels(row, 'study_types'))
        for mention in mentions(text, terms):
            kind = role(text, mention['start'], mention['end'])
            category = by_concept[mention['concept']].get('category')
            counts[kind] += 1
            if category and category not in declared:
                pair = (row['id'], category)
                novel.add(pair)
                if kind == 'target_candidate':
                    held.add(pair)
            details.append({'id': row['id'], **mention, 'role': kind, 'category_hint': category})
    return {'mentions': len(details), 'roles': dict(counts), 'novel_direct_category_pairs': len(novel),
            'novel_direct_pairs_with_target_cue': len(held), 'rows': details,
            'boundary': 'Lexical context cues and direct category hints only; not validated roles or accepted study types.'}


def validate_folds(rows, ids):
    by_id = {r['id']: i for i,r in enumerate(rows)}
    if len(by_id) != len(rows) or not ids or sorted(k for fold in ids for k in fold) != sorted(by_id):
        raise ValueError('fold coverage mismatch')
    g = groups(rows)
    assigned = {}
    splits = []
    for number, fold in enumerate(ids):
        if not fold or len(fold) == len(rows):
            raise ValueError('invalid empty training/test fold')
        test = sorted(by_id[k] for k in fold)
        train = sorted(set(range(len(rows))) - set(test))
        for i in test:
            if assigned.setdefault(g[i], number) != number:
                raise ValueError('proxy group crossed folds')
        splits.append((train, test))
    return splits


def fit_predict(train, test, known, method):
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import normalize

    if method not in METHODS or train.shape[0] != len(known):
        raise ValueError('invalid classifier input')
    selected = [i for i, y in enumerate(known) if y]
    if not selected:
        return [[] for _ in range(test.shape[0])]
    train, test = normalize(train[selected]), normalize(test)
    known = [known[i] for i in selected]
    if method == 'knn':
        scores = test @ train.T
        if hasattr(scores, 'toarray'):
            scores = scores.toarray()
        out = []
        for row in scores:
            votes = Counter()
            for j in sorted(range(len(row)), key=lambda j: (-row[j], j))[:5]:
                if row[j] > 0:
                    for label in known[j]:
                        votes[label] += float(row[j])
            out.append(rank_scores(votes)[:5])
        return out
    vocab = sorted({k for labels_ in known for k in labels_})
    scores = {}
    for label in vocab:
        y = np.asarray([label in values for values in known])
        if y.all():
            scores[label] = np.ones(test.shape[0])
        else:
            model = LogisticRegression(C=1.0, solver='liblinear', random_state=17,
                                       class_weight='balanced' if method == 'balanced' else None,
                                       max_iter=1000).fit(train, y)
            scores[label] = model.predict_proba(test)[:, 1]
    return [rank_scores({k: v[i] for k,v in scores.items()})[:5] for i in range(test.shape[0])]


def paired(baseline, challenger):
    a = {r['id']: r for r in baseline}
    b = {r['id']: r for r in challenger}
    if len(a) != len(baseline) or len(b) != len(challenger) or set(a) != set(b) or any(a[k]['gold'] != b[k]['gold'] for k in a):
        raise ValueError('paired identity/reference mismatch')
    result = dict(shared=0, gains=0, losses=0, missed_both=0)
    for k, row in a.items():
        gold = set(row['gold'])
        first, second = gold & set(row['ranking'][:3]), gold & set(b[k]['ranking'][:3])
        result['shared'] += len(first & second)
        result['gains'] += len(second-first)
        result['losses'] += len(first-second)
        result['missed_both'] += len(gold-(first|second))
    return result


def decode_fold_assignment(rows, assignment, count):
    if len(assignment) != len(rows) or set(assignment) != set(map(str, range(count))):
        raise ValueError('invalid fold assignment')
    return [[row['id'] for row, fold in zip(rows, assignment, strict=True) if fold == str(i)]
            for i in range(count)]


def fold_inventory(catalogue):
    rows = sorted((r for r in catalogue['guidelines'] if r.get('title')), key=lambda r: r['id'])
    result = {'catalogue_sha256': MEMBER_SHA, 'previous_report_sha256': PREVIOUS_SHA,
              'test_ids': decode_fold_assignment(rows, FOLD_ASSIGNMENT, 5)}
    raw = (json.dumps(result, indent=2)+'\n').encode()
    if hashlib.sha256(raw).hexdigest() != FOLDS_SHA:
        raise ValueError('retained fold identity mismatch')
    return result


def embed_titles(rows, embed, dimension):
    import numpy as np

    rows = sorted((r for r in rows if r.get('title')), key=lambda r: r['id'])
    if not rows or len(rows) != len({r['id'] for r in rows}):
        raise ValueError('embedding identity mismatch')
    start = time.perf_counter()
    vectors = []
    for row in rows:
        vector = np.asarray(embed(row['title']), dtype=np.float64)
        if vector.shape != (dimension,) or not np.isfinite(vector).all():
            raise ValueError('invalid embedding shape or values')
        norm = np.linalg.norm(vector)
        if not np.isfinite(norm) or norm == 0:
            raise ValueError('invalid embedding norm')
        vectors.append(vector/norm)
    matrix = np.asarray(vectors, dtype='<f8')
    return matrix, {'ids': [r['id'] for r in rows], 'requests': len(rows),
                    'dimension': dimension, 'seconds': time.perf_counter()-start,
                    'matrix_sha256': hashlib.sha256(matrix.tobytes()).hexdigest()}


def run(catalogue, fold_ids, *, dense=None):
    import numpy as np
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer

    rows = sorted(catalogue['guidelines'], key=lambda r: r['id'])
    if len(rows) != catalogue['published_count'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('catalogue identity mismatch')
    valid = [r for r in rows if r.get('title')]
    splits = validate_folds(valid, fold_ids)
    reps = ('word-tfidf', 'char-tfidf', *sorted(dense or {}))
    if dense is not None and set(dense) & {'word-tfidf','char-tfidf'}:
        raise ValueError('reserved representation name')
    if dense is not None:
        for name, vectors in dense.items():
            if vectors.ndim != 2 or vectors.shape[0] != len(valid) or not np.isfinite(vectors).all() or not np.all(np.linalg.norm(vectors, axis=1) > 0):
                raise ValueError(f'invalid embedding matrix: {name}')
    arms = {}
    for rep in reps:
        observations = {method: {f: {} for f in FACETS} for method in METHODS}
        seconds = Counter()
        dimensions = []
        for train, test in splits:
            started = time.perf_counter()
            if rep in ('word-tfidf','char-tfidf'):
                analyzer = rep.split('-')[0]
                vectorizer = TfidfVectorizer(analyzer=analyzer, ngram_range=(1,2) if analyzer == 'word' else (3,5))
                a = vectorizer.fit_transform([valid[i]['title'] for i in train])
                b = vectorizer.transform([valid[i]['title'] for i in test])
            else:
                a, b = dense[rep][train], dense[rep][test]
            dimensions.append(a.shape[1])
            seconds['representation'] += time.perf_counter()-started
            for method in METHODS:
                for f in FACETS:
                    started = time.perf_counter()
                    ranks = fit_predict(a,b,[labels(valid[i],f) for i in train],method)
                    observations[method][f].update((valid[i]['id'],rank) for i,rank in zip(test,ranks,strict=True))
                    seconds[method] += time.perf_counter()-started
        for method in METHODS:
            facets = {}
            for f in FACETS:
                detail = [{'id': r['id'], 'gold': labels(r,f), 'ranking': observations[method][f].get(r['id'],[])} for r in rows]
                facets[f] = {'metrics': evaluate(detail), 'rows': detail}
            arms[f'{rep}/{method}'] = {'dimensions': dimensions, 'representation_seconds': seconds['representation'],
                                       'classifier_seconds': seconds[method], 'facets': facets}
    for arm in arms.values():
        incumbent = arms.get('char-tfidf/knn', next(iter(arms.values())))
        for f in FACETS:
            arm['facets'][f]['paired_vs_incumbent_at_3'] = paired(incumbent['facets'][f]['rows'],arm['facets'][f]['rows'])
    return {'source_revision': catalogue['source_revision'], 'directory_entries': len(rows), 'titles': len(valid),
            'fold_ids': fold_ids, 'arms': arms, 'versions': {'numpy': np.__version__, 'sklearn': sklearn.__version__},
            'boundary': 'Exploratory catalogue-relative label ranking; unknown-only rows excluded from facet training. Other recorded labels are weak negatives, not independently established absences.'}


def read_catalogue(path, member=False):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != (MEMBER_SHA if member else ARCHIVE_SHA):
        raise ValueError('catalogue bytes differ')
    if member:
        return json.loads(raw)
    with zipfile.ZipFile(path) as z:
        return json.loads(z.read('equator-catalogue.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue',type=Path,required=True)
    parser.add_argument('--member',action='store_true')
    parser.add_argument('--folds',type=Path)
    parser.add_argument('--backend', choices=('classical','bge','qwen'), default='classical')
    parser.add_argument('--assets',type=Path)
    parser.add_argument('--terms',type=Path,default=Path(__file__).with_name('mesh-selected-v1.json'))
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    cat = read_catalogue(args.catalogue,args.member)
    raw = args.terms.read_bytes()
    if hashlib.sha256(raw).hexdigest() != TERMS_SHA:
        raise ValueError('descriptor projection digest mismatch')
    folds = fold_inventory(cat)
    if args.folds and hashlib.sha256(args.folds.read_bytes()).hexdigest() != FOLDS_SHA:
        raise ValueError('fold source mismatch')
    dense = None
    receipt = None
    if args.backend == 'bge':
        from scripts.costing_retrieval import LocalRanker

        if args.assets is None:
            raise ValueError('BGE needs verified local assets')
        model = LocalRanker(args.assets, 'bge')
        matrix, receipt = embed_titles(cat['guidelines'], model, 384)
        receipt.update(model='bge-small-en-v1.5', asset_hashes=model.asset_hashes,
                       runtime=model.version)
        dense = {'bge-raw':matrix}
    elif args.backend == 'qwen':
        import requests
        from scripts.hosted_specialist_development import make_post
        from scripts.task_framing import EMBED_MODEL, embedding_vector

        with requests.Session() as session:
            session.trust_env = False
            post = make_post(session, 'http://127.0.0.1:18883/v1/embeddings', None, 719)
            def embed(text):
                return embedding_vector(post({'model': EMBED_MODEL, 'input': text}))
            matrix, receipt = embed_titles(cat['guidelines'], embed, 1024)
        receipt['model'] = EMBED_MODEL
        dense = {'qwen-raw':matrix}
    report = run(cat, folds['test_ids'], dense=dense)
    report['embedding'] = receipt
    report['role_audit'] = role_audit(cat['guidelines'],json.loads(raw)['terms'])
    report.update(catalogue_sha256=MEMBER_SHA, folds_sha256=FOLDS_SHA,
                  terms_sha256=TERMS_SHA, implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
