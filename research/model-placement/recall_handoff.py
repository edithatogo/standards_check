"""Shared positive-level audit imports. Development diagnostics, no cross-cohort pooling."""
import argparse
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from recall_audit import STAGES, first_failure, stage_counts

PINS = {
    15100692740: 'f7155c826e7e9e601855f8e54e38220e185c05f622429e029205fb7e7261d7a6',
    15105999587: 'd4e7b997346976c6eb5aa118ef6cf6a4536824e459931a5a2bf0221bc50f12cc',
    15105947458: 'f30563e5c866fc7408987a07abd3a0014490dc263ceeb9e441fafc82c3b8534a',
    15106112148: 'e5f3d8a17ce8b57169aa19f7730b1d2f272c04d23282e8240822539d3b55f09f',
    15106576904: '4133e229f7b6965e17690e063ebecd745ed96671b1fd8ce8247acedd2455a846',
}
HEADING_PIN = 'd7fbc4c805eb31f67fbbf2a7d1aee7aea4317626c59b28895f943075a4a991d2'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def case_id(namespace, reference_digest, original_id):
    # Not derived from prediction, arm, a mutable label, or ordinal row position.
    return digest([namespace,reference_digest,original_id])


def row(namespace,tier,reference_digest,original_id,arm,observed,receipt,**extra):
    states={s:'unknown' for s in STAGES};states.update(observed)
    first,established=first_failure(states)
    return {'case_id':case_id(namespace,reference_digest,original_id),'namespace':namespace,
            'reference_tier':tier,'reference_digest':reference_digest,'original_id':original_id,
            'arm':arm,'receipt':receipt,'stages':states,'first_observed':first,'first_established':established,**extra}


def members(root,ident,names):
    path=root/f'github-actions-artifact-{ident}.zip'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=PINS[ident]:raise ValueError('artifact digest mismatch')
    with zipfile.ZipFile(path) as z:return {n:json.loads(z.read(n)) for n in names}


def common_misses(audit):
    def flags(arm):
        rs=audit['arms'][arm]['rows']; result={tuple(r['id']):r['stages']['candidate_generation']=='fail' for r in rs}
        if len(result)!=len(rs):raise ValueError('duplicate positive')
        return result
    a,b=flags('bge'),flags('instructed_qwen_bge')
    if set(a)!=set(b):raise ValueError('positive universe mismatch')
    orders={tuple(r['id']):r['orders'] for r in audit['full_rankings']};records=[]
    for key in sorted(k for k in a if a[k] and b[k]):
        q,t=key[:2],key[2];ranks={n:o.index(t)+1 for n,o in orders[q].items()}
        records.append({'original_id':list(key),'full_ranks':ranks})
    return {'n':len(records),'by_instrument':dict(Counter(r['original_id'][0] for r in records)),
            'by_domain':dict(Counter(r['original_id'][2] for r in records)),
            'lexical_top10':sum(r['full_ranks']['exact_lexical']<=10 for r in records),
            'parent_proxy_top10':sum(r['full_ranks']['exact_parent_topic_proxy']<=10 for r in records),
            'best_dense_rank_le15':sum(min(r['full_ranks']['bge'],r['full_ranks']['instructed_qwen_bge'])<=15 for r in records),
            'records':records,'boundary':'Editorial misses, not causal errors or independently established positives.'}


def collect(root,audit,heading=None):
    if audit['reference_status']!='editorial_positive_only' or audit['independent_positive_count']!=0:raise ValueError('unqualified input audit')
    rows=[]; notes={}
    tier='synthetic_author_labelled'
    # Existing costing receipt; convert to same envelope, not another retrieval run.
    ref=digest(audit['source_input_pins'])
    for arm,entry in audit['arms'].items():
        for r in entry['rows']:
            rows.append(row('costing', 'editorial_positive_only',ref,r['id'],arm,r['stages'],'recall_audit:three_pinned_artifacts',candidate_rank=r['candidate_rank'],review_rank=r['review_rank'],candidate_budget=10,review_budget=5))
    # Source-anchor facts (row, nested edge, footnote, qualifier edge); preserve separate units.
    e9=members(root,15100692740,('pdfplumber.json','poppler.json'))
    if e9['pdfplumber.json']['cases'].keys()!=e9['poppler.json']['cases'].keys():raise ValueError('E9 case coverage mismatch')
    for file,report in e9.items():
        for key,c in report['cases'].items():
            prior=e9['pdfplumber.json']['cases'][key]
            if c['source_sha256']!=prior['source_sha256'] or c['reference']!=prior['reference']:raise ValueError('E9 reference mismatch')
            expected=Counter(tuple(f) for f,_ in c['reference'])
            if any(n!=1 for n in expected.values()):raise ValueError('duplicate reference fact')
            predicted=Counter(tuple(f) for f,_ in c['predictions'])
            for fact,box in c['reference']:
                k,page,item,content=fact; hit=predicted[tuple(fact)]>0
                matches=[{'content_digest':digest(f[3]),'locator':loc} for f,loc in c['predictions'] if f[:3]==fact[:3]]
                detail='exact_fact' if hit else 'content_corruption' if matches else 'missing_fact'
                rows.append(row('E9',tier,c['source_sha256'],[key,k,page,item,digest(content)],report['reader'],{'source_anchor':'pass' if hit else 'fail'},f'15100692740/{file}',unit=k,expected_region=box,observed_anchors=matches,detail=detail))
    # Exact typed spans, not independent clause-level decisions.
    e10=members(root,15105999587,('rules.json','gliner.json','frame-clause-names.json','frame-operator-first.json'))
    baseline=e10['rules.json'];expected_cases={c['id']:c for c in baseline['cases']}
    for file,report in e10.items():
        if report['fixture_sha256']!=baseline['fixture_sha256'] or {c['id'] for c in report['cases']}!=set(expected_cases):raise ValueError('E10 fixture mismatch')
        for c in report['cases']:
            prior=expected_cases[c['id']]
            if any(c[k]!=prior[k] for k in ('text','family','expected')):raise ValueError('E10 reference mismatch')
            for kind,start,end in c['expected']:
                hit=[kind,start,end] in c['predicted']
                rows.append(row('E10',tier,report['fixture_sha256'],[c['id'],kind,start,end],report.get('frame',report['arm']),{'source_anchor':'pass' if hit else 'fail'},f'15105999587/{file}',unit='typed_span',source_text_digest=digest(c['text']),family=c['family'],observed_spans=c['predicted'],detail='exact_span' if hit else 'missing_exact_span',invalid_output=bool(c['invalid_abstention'])))
    # E11 reference positives only; ranking stage is not evidence discharge.
    e11=members(root,15105947458,('ablation.json','comparison.json'));fixture=e11['comparison.json']['fixture_sha256']
    expected_pairs={}
    def graph_rows(method,name,records,receipt):
        pairs={(r['instrument_id'],r['item_id'],t) for r in records for t in r['reference']}
        if method in expected_pairs and pairs!=expected_pairs[method]:raise ValueError('E11 positive universe mismatch')
        expected_pairs[method]=pairs
        for r in records:
            order=r['ranking'];q=[r['instrument_id'],r['item_id']];original=r.get('original_pool',order[:10])
            if len(order)!=len(set(order)) or len(original)!=len(set(original)) or set(original)!=set(order[:10]):raise ValueError('pool or ranking mismatch')
            for t in r['reference']:
                rank=order.index(t)+1 if t in order else None;pool=t in original
                rows.append(row('E11',tier,fixture,[*q,t],method+'/'+name,{'candidate_generation':'pass' if pool else 'fail','rank_cutoff':('pass' if rank<=5 else 'fail') if pool else 'not_reached'},receipt,unit='relevance_association',candidate_rank=original.index(t)+1 if pool else None,review_rank=rank if pool else None,candidate_budget=10,review_budget=5,returned_pool_slots=len(original)))
    for method,entry in e11['ablation.json']['methods'].items():
        for name,arm in entry['arms'].items():graph_rows(method,name,arm['evaluation']['rows'],'15105947458/ablation.json')
    if heading is not None:
        if hashlib.sha256(heading.read_bytes()).hexdigest()!=HEADING_PIN:raise ValueError('heading digest mismatch')
        h=json.loads(heading.read_bytes())
        if h['fixture_sha256']!=fixture:raise ValueError('heading fixture mismatch')
        for method,entry in h['methods'].items():
            for name in ('heading_text_generation','heading_text_fixed_pool'):
                graph_rows(method,name,[{'instrument_id':r['id'][0],'item_id':r['id'][1],'reference':r['reference'],'ranking':r['rankings'][name],'original_pool':r['rankings']['baseline'] if name.endswith('fixed_pool') else r['rankings'][name]} for r in entry['records']],f'#185/graph-context-receipt.json:{HEADING_PIN}')
    else:notes['heading']='not supplied; no invented output or rerun'
    # E12 Offline synthetic equivalence positives. Fragment ranks do not equal pair retrieval.
    off=members(root,15106112148,('report.json',))['report.json']
    if off['review_resolved']!=0:raise ValueError('review resolution requires separate adjudication receipt')
    for c in off['cases']:
        if c['reference']!='equivalent':continue
        for state,s in c['states'].items():
            for method in ('strict_nli','proof_required'):
                pred=s['predictions'][method]
                rows.append(row('E12-offline',tier,off['fixture_sha256'],[c['id'],'pair'],state+'/'+method,{'evidence':'pass' if s['complete'] else 'fail','decision':'pass' if pred=='equivalent' else 'fail'},'15106112148/report.json',unit='synthetic_equivalent_pair',family=c['family'],split=c['split'],evidence_ids=s['evidence_ids'],decision_detail=pred,proof_status=s['proof']['status'],review_resolved=False))
    intake=members(root,15106576904,('priority-retry.json',))['priority-retry.json']
    holds=[{'edition':r['edition'],'status':r['status'],'reason':r.get('reason'),'attempts':r.get('acquisition',{}).get('attempts',[])} for r in intake['editions']]
    # Proposed PRISMA controls receive stable namespace IDs only; never counted as observed cases.
    proposals=[];pack='git-blob:318b0786e195ee9b6ccb5b0a39ade117ce3c6a2c'
    for key,anchors in [('methods-results',['13d','20b']),('automation-scope',['8','9','11']),('parent-child',['20b']),('complete-bundle',['20b']),('sought-collected',['10a']),('registration-protocol',['24a','24b']),('analysis-level',['19','20b']),('heterogeneity-sensitivity',['13e','20c','13f','20d']),('source-only-evidence',['20b'])]:
        proposals.append({'case_id':case_id('PRISMA-proposed',pack,[key,anchors]),'original_id':key,'anchors':['prisma-2020-checklist:item:'+x for x in anchors],'source_pin':pack,'status':'proposed_not_executed','reference_tier':'unadjudicated_synthetic_proposal','receipt':'#158/comment/7189300653'})
    groups=defaultdict(lambda:defaultdict(list));seen=set()
    for r in rows:
        key=(r['case_id'],r['arm'])
        if key in seen:raise ValueError('duplicate case/arm')
        seen.add(key);groups[r['namespace']][r['arm']].append(r)
    summary={n:{a:stage_counts(rs) for a,rs in arms.items()} for n,arms in groups.items()}
    return {'protocol':'shared-missed-match-development-v1','independent_positive_count':0,'scientific_qualification':False,'semantic_merges':0,'artifact_pins':PINS,'rows':rows,'summary':summary,'proposed_controls':proposals,'intake_holds':holds,'common_misses':common_misses(audit),'notes':notes,'boundary':'Separate cohorts and positive units. No cross-cohort end-to-end attribution, no independent labels, no new runs or source text.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--heading',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.write_text(json.dumps(collect(a.artifacts,json.loads(a.audit.read_bytes()),a.heading),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
