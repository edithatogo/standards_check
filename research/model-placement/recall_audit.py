"""Shared positive-match recall audit, development only; no canonical schema changes."""
import argparse
import hashlib
import itertools
import json
import resource
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from scripts.lexical_text import cosine, normalise, term_counts, tfidf_vectors

STAGES = ('source_anchor','candidate_generation','rank_cutoff','evidence','decision')
STATES = {'pass','fail','unknown','not_reached'}
PINS = {
    15088716936:'3df9b23127cf07cc67c55ccd18ce942895d70a62769015699cd2af1c95cdb20e',
    15090704998:'194ed70304518cea956e60970ff337ac5d4cd486ba64de0a4753574a66aed77f',
    15105542356:'1d8fefd7f760444e0df99b733d050bc7ecc386a377b060b2cfc136c5613247b3',
}
INPUTS = {'costing-standards-registry.json':'dba42197db8a317e07e18b32f718e38ccdc648a40370240d804423e3940f5378','costing-item-mappings.json':'757606b5f703f18eca0474a3a4f6ebf1ed5270e5b867a305c6df67869c2819f1'}


def first_failure(states):
    if set(states)!=set(STAGES) or not set(states.values())<=STATES:
        raise ValueError('invalid stage states')
    for i,s in enumerate(STAGES):
        if states[s]=='fail':
            return s, s if all(states[t]=='pass' for t in STAGES[:i]) else 'unresolved'
    return 'none_observed', 'none' if all(v=='pass' for v in states.values()) else 'unresolved'


def stage_counts(rows):
    first=Counter(); established=Counter(); counts={s:Counter() for s in STAGES}
    overlap={a+'|'+b:{'both_failed':0,'both_observed':0} for a,b in itertools.combinations(STAGES,2)}
    for row in rows:
        states=row['stages']; obs,conf=first_failure(states);first[obs]+=1;established[conf]+=1
        for s,v in states.items():counts[s][v]+=1
        for a,b in itertools.combinations(STAGES,2):
            o=overlap[a+'|'+b];o['both_failed']+=states[a]==states[b]=='fail';o['both_observed']+=states[a] in ('pass','fail') and states[b] in ('pass','fail')
    return {'first_observed':dict(first),'first_established':dict(established),'by_stage':{s:{v:c[v] for v in sorted(STATES)} for s,c in counts.items()},'overlap':overlap}


def audit_arm(refs,pools,rankings,*,review=5,pool_budget=10):
    if not refs or set(refs)!=set(pools) or set(refs)!=set(rankings) or not 0<review<=pool_budget:
        raise ValueError('invalid query or budget')
    for q,p in pools.items():
        r=rankings[q]
        if len(p)!=pool_budget or len(set(p))!=len(p) or len(r)!=len(p) or set(r)!=set(p):raise ValueError('pool drift or budget mismatch')
    rows=[]
    for q,expected in sorted(refs.items()):
        if not expected:raise ValueError('empty positive reference')
        for t in sorted(expected):
            in_pool=t in pools[q];in_review=t in rankings[q][:review]
            states={'source_anchor':'unknown','candidate_generation':'pass' if in_pool else 'fail','rank_cutoff':('pass' if in_review else 'fail') if in_pool else 'not_reached','evidence':'unknown','decision':'unknown'}
            obs,est=first_failure(states)
            rows.append({'id':[q[0],q[1],t],'candidate_rank':pools[q].index(t)+1 if in_pool else None,'review_rank':rankings[q].index(t)+1 if in_pool else None,'stages':states,'first_observed':obs,'first_established':est,'decision_detail':None})
    def metric(orders,k):
        hits={q:len(set(orders[q][:k])&g) for q,g in refs.items()};n=sum(map(len,refs.values()))
        return {'hits':sum(hits.values()),'positives':n,'micro_recall':sum(hits.values())/n,'macro_query_recall':sum(hits[q]/len(refs[q]) for q in refs)/len(refs),'slots':sum(len(orders[q][:k]) for q in refs)}
    return {'metrics':{**{f'r{k}':metric(rankings,k) for k in (1,3,5) if k<=pool_budget},'pool':metric(pools,pool_budget),'review':metric(rankings,review)},'failure_counts':stage_counts(rows),'rows':rows}


def exact_phrase(query,target):
    q,t=normalise(query),normalise(target)
    return bool(q and t and f' {q} ' in f' {t} ')


def parent_topics(queries):
    out={}
    for q in queries:
        instrument,item=q
        while '.' in item:
            item=item.rsplit('.',1)[0]
            if (instrument,item) in queries:
                out[q]=queries[instrument,item];break
    return out


def lexical(queries,targets,method):
    docs={('q',q):term_counts(v,method) for q,v in queries.items()}
    docs.update({('t',t):term_counts(v,method) for t,v in targets.items()})
    vectors=tfidf_vectors(docs);out={}
    for q in queries:
        scores={t:cosine(vectors.get(('q',q),{}),vectors.get(('t',t),{})) for t in targets}
        out[q]=[t for t in sorted(scores,key=lambda t:(-scores[t],t)) if scores[t]>0]
    return out


def rrf_rank(universe,orders,exact):
    scores=defaultdict(float)
    if not exact<=universe:raise ValueError('unknown exact candidate')
    for order in orders:
        if len(order)!=len(set(order)) or not set(order)<=universe:raise ValueError('invalid lexical order')
        for i,t in enumerate(order,1):scores[t]+=1/(60+i)
    return sorted(universe,key=lambda t:(-(t in exact),-scores[t],t))


def load(root,ident,member):
    p=root/f'github-actions-artifact-{ident}.zip'
    if hashlib.sha256(p.read_bytes()).hexdigest()!=PINS[ident]:raise ValueError('artifact digest mismatch')
    with zipfile.ZipFile(p) as z:return json.loads(z.read(member))


def project(root):
    paths={name:root/'reconciliations'/'costing'/name for name in INPUTS}
    if {n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}!=INPUTS:raise ValueError('source digest mismatch')
    r=json.loads(paths['costing-standards-registry.json'].read_bytes());m=json.loads(paths['costing-item-mappings.json'].read_bytes())
    return {'queries':[[x['instrument_id'],x['item_id'],x['topic']] for x in m['mappings']],'targets':[[x['id'],x['definition']] for x in r['domains']]}


def run(artifacts,inputs,*,projection_only=False):
    started=time.perf_counter();b=load(artifacts,15088716936,'paired.json');q=load(artifacts,15090704998,'report.json');m=load(artifacts,15105542356,'fixed-bge.json')
    if b['input_sha256']!=INPUTS or m['input_sha256']!=INPUTS or any(x['scientific_qualification'] or x['semantic_merges'] for x in (b,q,m)):raise ValueError('unexpected evidence status')
    def extract(result):
        rows=result['rows'];orders={(r['instrument_id'],r['item_id']):r['ranking'] for r in rows};refs={(r['instrument_id'],r['item_id']):set(r['reference']) for r in rows}
        if len(rows)!=len(orders):raise ValueError('duplicate query')
        return orders,refs
    bge,refs=extract(b['results']['bge']);qwen,qr=extract(q['results']['instruction-rrf-bge']);mini,mr=extract(m['result']);mp,mpr=extract(m['pool_incumbent']);word,wr=extract(b['results']['word']);char,cr=extract(b['results']['char'])
    if any(r!=refs for r in (qr,mr,mpr,wr,cr)) or len(refs)!=106 or sum(map(len,refs.values()))!=125:raise ValueError('reference mismatch')
    universe=set(next(iter(bge.values())))
    if len(universe)!=31 or any(len(o)!=31 or set(o)!=universe for ranks in (bge,qwen) for o in ranks.values()) or any(not r<=universe for r in refs.values()):raise ValueError('incomplete universe')
    if mp!={k:o[:10] for k,o in bge.items()}:raise ValueError('MiniLM pool drift')
    # Copy only label-free text; on a full checkout require exact source bytes.
    data=json.loads(inputs.read_bytes()) if projection_only else project(inputs)
    queries={(a,b):t for a,b,t in data['queries']};targets=dict(data['targets'])
    if set(queries)!=set(refs) or set(targets)!=universe or len(queries)!=len(data['queries']) or len(targets)!=len(data['targets']):raise ValueError('text identity mismatch')
    if lexical(queries,targets,'word')!=word or lexical(queries,targets,'char')!=char:raise ValueError('retained lexical ranks differ from text projection')
    parents=parent_topics(queries);context={k:(parents[k]+' '+v if k in parents else v) for k,v in queries.items()}
    cw,cc=lexical(context,targets,'word'),lexical(context,targets,'char')
    exact={k:{t for t,d in targets.items() if exact_phrase(v,d)} for k,v in queries.items()}
    simple={k:rrf_rank(universe,(word[k],char[k]),exact[k]) for k in refs}
    proxy={k:rrf_rank(universe,(cw[k],cc[k]),exact[k]) for k in refs}
    orders={'bge':bge,'instructed_qwen_bge':qwen,'exact_lexical':simple,'exact_parent_topic_proxy':proxy}
    pools={name:{k:o[:10] for k,o in rank.items()} for name,rank in orders.items()}
    arms={n:audit_arm(refs,p,p) for n,p in pools.items()};arms['bge_minilm']=audit_arm(refs,pools['bge'],mini)
    # Oracle uses reference labels after the ranking experiment. No operational credit.
    # Full enumeration is a 31-candidate diagnostic, not equal review cost.
    oracle={k:sorted(g)+sorted(universe-g) for k,g in refs.items()};op={k:o[:10] for k,o in oracle.items()}
    arms['label_oracle_at_budget']=audit_arm(refs,op,op)
    all31=audit_arm(refs,{k:sorted(universe) for k in refs},{k:sorted(universe) for k in refs},review=31,pool_budget=31)
    misses={n:{tuple(r['id']) for r in a['rows'] if r['first_observed'] in ('candidate_generation','rank_cutoff')} for n,a in arms.items()}
    pool_misses={n:{tuple(r['id']) for r in a['rows'] if r['stages']['candidate_generation']=='fail'} for n,a in arms.items()}
    def overlap(sets):return {a+'|'+b:{'shared_misses':len(sets[a]&sets[b]),'a_only':len(sets[a]-sets[b]),'b_only':len(sets[b]-sets[a])} for a,b in itertools.combinations(sets,2)}
    # True rerank losses vs *same* input order, not every rank-cutoff miss.
    rankloss=misses['bge_minilm']-misses['bge'];rankgain=misses['bge']-misses['bge_minilm']
    for n,a in arms.items():
        a['by_instrument']={i:stage_counts([r for r in a['rows'] if r['id'][0]==i]) for i in sorted({k[0] for k in refs})}
    return {'protocol':'shared-missed-match-development-v1','reference_status':'editorial_positive_only','independent_positive_count':0,'scientific_qualification':False,'semantic_merges':0,'pins':PINS,'source_input_pins':INPUTS,'projection_only':projection_only,'positive_unit':'instrument_id,item_id,target_domain_id','candidate_budget':10,'review_budget':5,'review_outcomes_observed':False,'all31_enumeration':all31['metrics']['pool'],'arms':arms,'miss_overlap_at_review':overlap(misses),'miss_overlap_at_pool':overlap(pool_misses),'rerank_loss_ids':sorted(rankloss),'rerank_gain_ids':sorted(rankgain),'parent_proxy_queries':[list(k) for k in sorted(parents)],'unsignalled_pool_slots':{'exact_lexical':sum(t not in set(word[k])|set(char[k])|exact[k] for k,o in pools['exact_lexical'].items() for t in o),'exact_parent_topic_proxy':sum(t not in set(cw[k])|set(cc[k])|exact[k] for k,o in pools['exact_parent_topic_proxy'].items() for t in o)},'full_rankings':[{ 'id':list(k),'known_positive_ids':sorted(refs[k]),'orders':{n:o[k] for n,o in orders.items()}} for k in sorted(refs)],'wall_seconds':time.perf_counter()-started,'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'fresh_model_download_bytes':0,'boundary':'No independent source/anchor or evidence/decision observations; unknown is not success. Full oracle label-aware diagnostic only. Parent topic from existing dotted item ID prefix is a proxy, not an anchored heading.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--projection-only',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(run(a.artifacts,a.inputs,projection_only=a.projection_only),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
