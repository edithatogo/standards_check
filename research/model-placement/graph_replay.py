"""Instrument-disjoint label-free co-retrieval graph replay; not a source ontology."""
import argparse
import itertools
import json
import math
import resource
import time
from collections import Counter
from pathlib import Path
from replay import load


def graph(rankings, universe, *, k=5):
    if not universe or not 2 <= k <= len(universe):
        raise ValueError('invalid graph budget')
    counts={c:Counter() for c in universe}
    for order in rankings:
        if len(order)!=len(set(order)) or not set(order)<=universe or len(order)<k:
            raise ValueError('invalid graph training ranking')
        for a,b in itertools.combinations(order[:k],2):
            counts[a][b]+=1; counts[b][a]+=1
    return {a:({b:n/sum(counts[a].values()) for b,n in sorted(counts[a].items())} if counts[a] else {a:1.0}) for a in sorted(universe)}


def propagation(order, g):
    if len(order)!=len(set(order)) or set(order)!=set(g):
        raise ValueError('graph universe mismatch')
    raw={c:1/(i+1) for i,c in enumerate(order)}; norm=math.fsum(raw.values()); seed={c:v/norm for c,v in raw.items()}
    def advance(p):
        result={c:0.7*seed[c] for c in g}
        for a,neighbors in g.items():
            for b,w in neighbors.items():result[b]+=0.3*p[a]*w
        return result
    one=advance(seed); walk=one
    for _ in range(7):walk=advance(walk)
    return one,walk


def evaluate(refs,before,after,*,ks=(1,3,5,10),fixed=False):
    if not refs or not set(refs)==set(before)==set(after):raise ValueError('query coverage mismatch')
    if any(len(x)!=len(set(x)) for orders in (before,after) for x in orders.values()):raise ValueError('duplicate candidate')
    if fixed and any(set(before[q])!=set(after[q]) for q in refs):raise ValueError('fixed pool drift')
    results={}; n=len(refs); total=sum(map(len,refs.values()))
    for k in ks:
        b={q:set(before[q][:k])&refs[q] for q in refs}; a={q:set(after[q][:k])&refs[q] for q in refs}
        results[str(k)]={'queries':n,'associations':total,'hits':sum(map(len,a.values())),'micro_recall':sum(map(len,a.values()))/total,'macro_query_recall':sum(len(a[q])/len(refs[q]) for q in refs)/n,'gains':sum(len(a[q]-b[q]) for q in refs),'losses':sum(len(b[q]-a[q]) for q in refs)}
    results['mrr']=sum(next((1/i for i,c in enumerate(after[q],1) if c in refs[q]),0) for q in refs)/n
    return results


def run(root):
    started=time.perf_counter(); prior=load(root,15088716936,'paired.json')['results']
    key=lambda r:(r['instrument_id'],r['item_id']); bge={key(r):r['ranking'] for r in prior['bge']['rows']}; refs={key(r):set(r['reference']) for r in prior['bge']['rows']}
    if set(bge)!=set(refs) or not bge:raise ValueError('query mismatch')
    universe=set(next(iter(bge.values())))
    if any(set(o)!=universe or len(o)!=len(universe) for o in bge.values()):raise ValueError('invalid universe')
    instruments=sorted({q[0] for q in bge}); ranks={a:{} for a in ('bge','one_hop_generation','diffusion_generation','one_hop_rerank','diffusion_rerank')}; folds={}; records=[]
    for instrument in instruments:
        test=sorted(q for q in bge if q[0]==instrument); training=sorted(q for q in bge if q[0]!=instrument)
        g=graph([bge[q] for q in training],universe); folds[instrument]={'training_queries':len(training),'test_queries':len(test),'training_instruments':sorted({q[0] for q in training}),'edge_count':sum(len(v) for a,v in g.items() if a not in v)//2,'adjacency':g}
        for q in test:
            one,walk=propagation(bge[q],g); order=lambda candidates,scores:sorted(candidates,key=lambda c:(-scores[c],c)); original=bge[q][:10]
            arms={'bge':original,'one_hop_generation':order(universe,one)[:10],'diffusion_generation':order(universe,walk)[:10],'one_hop_rerank':order(original,one),'diffusion_rerank':order(original,walk)}
            for a,o in arms.items():ranks[a][q]=o
            records.append({'id':list(q),'rankings':arms,'known_associations':sorted(refs[q]),'one_hop_scores':one,'diffusion_scores':walk})
    def summarize(ids):
        ref={q:refs[q] for q in ids}; base={q:ranks['bge'][q] for q in ids}; return {a:evaluate(ref,base,{q:r[q] for q in ids},fixed=a.endswith('rerank')) for a,r in ranks.items()}
    return {'protocol':'instrument-disjoint-co-retrieval-graph-v1','scientific_qualification':False,'semantic_merges':0,'model_download_bytes':0,'fresh_neural_inference':False,'boundary':'editorial positive association agreement; co-retrieval edges, not source hierarchy, ontology, or validated dependency links','folds':folds,'summary':summarize(sorted(bge)),'by_instrument':{i:summarize(sorted(q for q in bge if q[0]==i)) for i in instruments},'records':records,'wall_seconds':time.perf_counter()-started,'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--artifacts',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.write_text(json.dumps(run(args.artifacts),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
