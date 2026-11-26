"""Heading-text comparator and fixed-pool structural graph replay (E11 development only)."""
import argparse
import hashlib
import json
import math
import resource
import time
import zipfile
from pathlib import Path

from scripts.lexical_text import cosine, term_counts, tfidf_vectors

ARTIFACT = 'f3f106a3b8855eaf8d464fe638a15476327ee9d94411c445e52e3768fff05df2'
FIXTURE = '4aa25eb689a62a7b2758e19d6821f09708563a0d0c627c91b102cd84a3ca066d'


def contextualize(targets, parents, headings):
    if set(targets) != set(parents) or not set(parents.values()) <= set(headings):
        raise ValueError('missing source parent')
    return {t: headings[parents[t]] + '\n' + text for t, text in targets.items()}


def scores(queries, targets, method):
    docs = {('query', q): term_counts(text, method) for q, text in queries.items()}
    docs.update({('target', t): term_counts(text, method) for t, text in targets.items()})
    vectors = tfidf_vectors(docs)
    return {q: {t: cosine(vectors.get(('query', q), {}), vectors.get(('target', t), {})) for t in targets} for q in queries}


def rank(values, positive=True):
    if any(not math.isfinite(v) for v in values.values()):
        raise ValueError('invalid score')
    return sorted((t for t, s in values.items() if s > 0 or not positive), key=lambda t: (-values[t], t))


def fixed_pool(base, values):
    if set(base) != set(values) or any(len(p) != len(set(p)) or not set(p) <= set(values[q]) for q, p in base.items()):
        raise ValueError('fixed pool mismatch')
    return {q: rank({t: values[q][t] for t in p}, positive=False) for q, p in base.items()}


def paired(ref, base, after, k):
    if not ref or not set(ref) == set(base) == set(after) or any(not r for r in ref.values()):
        raise ValueError('reference mismatch')
    if any(len(o) != len(set(o)) for orders in (base, after) for o in orders.values()):
        raise ValueError('duplicate candidates')
    a = {q: set(after[q][:k]) & ref[q] for q in ref}
    b = {q: set(base[q][:k]) & ref[q] for q in ref}
    hits = sum(map(len, a.values()))
    return {'gains': sum(len(a[q]-b[q]) for q in ref), 'losses': sum(len(b[q]-a[q]) for q in ref), 'hits': hits,
            'macro_query_recall': sum(len(a[q])/len(ref[q]) for q in ref)/len(ref), 'precision': hits/(len(ref)*k), 'returned_slots': sum(len(after[q][:k]) for q in ref)}


def run(artifact, fixture):
    started = time.perf_counter()
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != ARTIFACT:
        raise ValueError('artifact digest mismatch')
    raw = fixture.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE:
        raise ValueError('fixture digest mismatch')
    data = json.loads(raw)
    with zipfile.ZipFile(artifact) as z:
        historical = json.loads(z.read('comparison.json'))
        revision = z.read('revision.txt').decode().strip()
    if historical['fixture_sha256'] != FIXTURE or historical['equivalence_inferred']:
        raise ValueError('invalid historical receipt')
    queries = {(r['family'], r['id']):r['text'] for r in data['queries']}
    targets = {r['id']:r['text'] for r in data['targets']}
    headings = {r['id']:r['text'] for r in data['headings']}
    parents = {r['id']:r['heading'] for r in data['targets']}
    refs = {(r['family'],r['id']):set(r['relevant']) for r in data['queries']}
    enriched = contextualize(targets, parents, headings)
    result = {}
    for method in ('word','char'):
        base = scores(queries,targets,method)
        context = scores(queries,headings,method)
        appended = scores(queries,enriched,method)
        parent = {q: {t:round(s + historical['fixed_bonus']*context[q][parents[t]],6) for t,s in row.items()} for q,row in base.items()}
        records = historical['methods'][method]['paired']
        historic_base = {(r['family'],r['query']):r['lexical_scores'] for r in records}
        full = {(r['family'],r['query']):r['graph_scores'] for r in records}
        historic_ref = {(r['family'],r['query']):set(r['reference']) for r in records}
        if base != historic_base or refs != historic_ref or set(full) != set(base) or any(set(s) != set(targets) for s in full.values()):
            raise ValueError('historical scores or reference mismatch')
        baseline = {q: rank(s)[:10] for q,s in base.items()}
        variants = {'parent':parent,'full_graph':full,'heading_text':appended}
        rankings = {'baseline':baseline}
        for name, v in variants.items():
            rankings[name+'_generation']={q:rank(s)[:10] for q,s in v.items()}
            rankings[name+'_fixed_pool']=fixed_pool(baseline,v)
        def summarize(keys):
            reference={q:refs[q] for q in keys}; b={q:baseline[q] for q in keys}
            return {a:{str(k):paired(reference,b,{q:orders[q] for q in keys},k) for k in (1,3,5,10)} for a,orders in rankings.items()}
        result[method]={'summary':summarize(sorted(refs)), 'by_family':{f:summarize(sorted(q for q in refs if q[0]==f)) for f in sorted({q[0] for q in refs})}, 'records':[{'id':list(q),'reference':sorted(refs[q]),'rankings':{a:r[q] for a,r in rankings.items()},'scores':{'baseline':base[q],**{a:s[q] for a,s in variants.items()}}} for q in sorted(refs)]}
    return {'protocol':'e11-heading-context-replay-v1','scientific_qualification':False,'semantic_merges':0,'fresh_model_download_bytes':0,'artifact_sha256':ARTIFACT,'fixture_sha256':FIXTURE,'source_revision':revision,'methods':result,'wall_seconds':time.perf_counter()-started,'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'boundary':'Exposed author-labelled synthetic fixture; simple lexical context vs graph, no source or independent qualification.'}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--artifact',type=Path,required=True); p.add_argument('--fixture',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    a.output.write_text(json.dumps(run(a.artifact,a.fixture),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
