"""Searchright-first, receipt-bound gap planning. No implicit legacy execution."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from bibliographic_recovery import digest, ident, index, normal_title
from searchright_bridge import read_pinned
from recovery_batch import choose_batch, summarize_batch

EARLY = '12a009fdcdfd8174daacfb606cb97a5c2648940c80df733a3b55a24ff6a14460'
CURRENT = '21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01'
CANARY = 'c409624a581a6d637e4ef19cca41ec5c82c6877ee1054b9750289158771627e1'
SEARCHRIGHT_REVISION = '444c5199c0887c0259fe47c3d2545b5c6b877d6d'
SCHEMA_PINS = {'strategy':'c2fea7532f6e3d40df12fee69d2f0c25cf8e4326', 'ast':'62c46dfd151476a3a5c00e76ad6e59201e40c747', 'compiled':'fdce39827363c601ba78f34dfd641823f6d31b3e'}
GAPS = {'missing_identifier', 'lookup_incomplete', 'unresolved_identifier', 'identifier_conflict'}
PROVIDERS = {'doi': ('crossref','open_alex'), 'pmid': ('pub_med','europe_pmc','open_alex'), 'pmcid': ('europe_pmc',), 'title': ('crossref','open_alex','pub_med','europe_pmc')}
PROVIDER_IDS = {'pub_med':'pubmed', 'europe_pmc':'europe-pmc', 'crossref':'crossref', 'open_alex':'openalex'}
CLI_DIALECTS = {'pub_med':'pubmed','europe_pmc':'europe-pmc','crossref':'crossref','open_alex':'openalex'}
OBSERVED_PROVIDER = {'crossref':'crossref','openalex':'open_alex','europe_pmc':'europe_pmc'}


def member(path, pin, name):
    if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
        raise ValueError('archive digest mismatch')
    with zipfile.ZipFile(path) as z:
        return json.loads(z.read(name))


def gap_audit(early, current, recovery):
    if current['source_revision'] != recovery['source_revision']:
        raise ValueError('source revision binding mismatch')
    a,b,c = index(early['records']), index(current['records']), index(recovery['rows'])
    if set(b)!=set(c):
        raise ValueError('current denominator binding mismatch')
    observed=defaultdict(list)
    for task in recovery.get('observations',[]):
        for key in task['catalogue_ids']:
            if key not in b:
                raise ValueError('observation outside catalogue')
            observed[key].extend({'kind':task['kind'],'value':task['value'],'provider':o['provider'],'status':o['result']['status'],'response_sha256':o.get('response_sha256')} for o in task['observations'])
    rows=[]
    for key,x in sorted(b.items()):
        y=c[key]; old=a.get(key)
        if x['source_blob_sha']!=y['source_blob_sha'] or x['status']!=y['status']:
            raise ValueError('record binding mismatch')
        same=old is not None and old['source_blob_sha']==x['source_blob_sha']
        current_gap=x['status'] in GAPS or y['identity_conflict']
        persistent=same and old['status'] in GAPS and x['status'] in GAPS
        rows.append({'id':key,'title':y['title'],'source_blob_sha':x['source_blob_sha'],'earlier_status':old['status'] if old else None,'current_status':x['status'],'unchanged_source':same,'current_identity_gap':current_gap,'persistent_identity_gap':persistent,'route': 'identity_hold' if y['identity_conflict'] else y['route'],'later_metadata_observations':observed[key],'independent_source_qualified':False})
    persistent=[r for r in rows if r['persistent_identity_gap']]
    return {'earlier_revision':early['source_revision'],'current_revision':current['source_revision'],'summary':{'earlier_rows':len(a),'current_rows':len(b),'unchanged_catalogue_rows':sum(r['unchanged_source'] for r in rows),'new_ids':sorted(set(b)-set(a)),'absent_ids':sorted(set(a)-set(b)),'current_identity_gaps':sum(r['current_identity_gap'] for r in rows),'persistent_identity_gaps':len(persistent),'persistent_statuses':dict(Counter(r['current_status'] for r in persistent)),'persistent_routes':dict(Counter(r['route'] for r in persistent)),'unchanged_transitions':dict(Counter(r['earlier_status']+' -> '+r['current_status'] for r in rows if r['unchanged_source']))},'rows':rows,'boundary':'Persistent means same catalogue ID and source blob unresolved at both survey revisions. Later metadata leads are not qualified editions or independent source/reference locks.'}


def plan_searches(audit,recovery):
    by_id=index(recovery['rows']); work=defaultdict(set); non_search=[]
    attempts={(OBSERVED_PROVIDER[o['provider']],t['kind'],t['value']) for t in recovery.get('observations',[]) for o in t['observations'] if o['provider'] in OBSERVED_PROVIDER and o['result']['status']!='deferred_circuit_breaker'}
    for row in audit['rows']:
        if not row['current_identity_gap']:
            continue
        r=by_id[row['id']]; route=row['route']
        if route in ('identity_hold','issuer_asset_candidate','issuer_landing_candidate','manual_identity_hold'):
            non_search.append({'id':row['id'],'route':route,'owner':'layout_source_qualification'});continue
        tokens=set(r['publication_identity'])|set(r['link_identifier_candidates'])
        candidates=[]
        for token in sorted(tokens):
            kind,sep,value=token.partition(':')
            if sep and kind in ('doi','pmid','pmcid') and ident(kind,value)==value:
                candidates.append((kind,value))
        title=r['title']
        if not candidates and isinstance(title,str) and 0<len(title)<=500 and not any(ord(c)<32 or ord(c)==127 for c in title):
            candidates.append(('title',title))
        if not candidates:
            non_search.append({'id':row['id'],'route':'manual_identity_hold','owner':'layout_source_qualification'});continue
        for kind,value in candidates:
            for dialect in PROVIDERS[kind]:
                work[(dialect,kind,value)].add(row['id'])
    # Prior provider+query attempts stay visible. New dialects are distinct leads;
    # neither a timeout nor a successful hit warrants repeating the same query now.
    strategies=[];excluded=[];persistent={r['id'] for r in audit['rows'] if r['persistent_identity_gap']}
    for (dialect,kind,value),ids in sorted(work.items()):
        if (dialect,kind,value) in attempts:
            excluded.append({'dialect':dialect,'kind':kind,'value':value,'catalogue_ids':sorted(ids)});continue
        strategy_id='recovery-'+digest([audit['current_revision'],dialect,kind,value,sorted(ids)])[:32]
        strategy={'schema_version':'org.searchright.search-strategy.v1','strategy_id':strategy_id,'review_id':'standardflow-bibliographic-recovery','source_id':PROVIDER_IDS[dialect],'dialect':dialect,'query':{'op':'term','term':{'text':value,'fields':['title' if kind=='title' else 'identifier'],'vocabulary':None,'explode':False,'phrase':True,'truncation':False}},'limits':{'publication_date':None,'languages':[],'publication_types':[],'filters':[],'rationale':[]},'translated_from':None,'notes':['Candidate publication discovery only; verify exact edition and source independently.','Do not execute degraded or review-required translations.']}
        strategies.append({'strategy':strategy,'strategy_sha256':digest(strategy),'catalogue_ids':sorted(ids),'persistent_ids':sorted(ids&persistent),'kind':kind,'postfilter':{'exact_identifier':None if kind=='title' else kind+':'+value,'candidate_only':True},'execution_authorized':False,'budget':{'max_records':3,'max_pages':1,'timeout_seconds':15,'max_retries':0}})
    # Retain the prior batch as an equal-slot planning comparator.
    queues=defaultdict(list)
    for x in sorted(strategies,key=lambda x:(-len(x['persistent_ids']),x['kind']=='title',x['strategy']['strategy_id'])):
        queues[x['strategy']['dialect']].append(x)
    old_batch=[]
    while any(queues.values()) and len(old_batch)<8:
        for dialect in sorted(queues):
            if queues[dialect] and len(old_batch)<8:
                old_batch.append(queues[dialect].pop(0)['strategy']['strategy_id'])
    observed = {row['id'] for row in audit['rows'] if any(o['status'] in ('exact_doi_metadata','exact_identifier_candidates') for o in row['later_metadata_observations'])}
    batch = choose_batch(strategies, already_observed=observed)
    batch_comparison = {'baseline_batch': old_batch, 'challenger_batch': batch,
                        'baseline': summarize_batch(strategies, old_batch),
                        'challenger': summarize_batch(strategies, batch),
                        'already_observed_metadata_leads': sorted(observed),
                        'boundary': 'Planning coverage only; no new search, hits, qualified edition or scientific improvement.'}
    return {'mechanism':'searchright','searchright_revision':SEARCHRIGHT_REVISION,'execution_status':'held_runtime_qualification','legacy_fallback':False,'strategies':strategies,'non_search_rows':non_search,'prior_attempts_excluded':len(excluded),'excluded_attempts':excluded,'next_bounded_batch':batch,'batch_comparison':batch_comparison,'reference_lock_received':False,'scientific_qualification':False,'boundary':'Native Searchright strategies only. Compile with an admitted pinned runtime; no query or document acquisition, implicit fallback, or source qualification.'}


def schema_registry(schemas):
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    return Registry().with_resources([(v['$id'],Resource.from_contents(v,default_specification=DRAFT202012)) for v in schemas.values()])


def compile_one(job,binary,pin,qualification,validator):
    """Offline compiler interface only; caller verifies real upstream qualification."""
    if not qualification or not qualification.strip():
        raise ValueError('runtime qualification receipt required')
    binary=binary.resolve(strict=True)
    if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest()!=pin:
        raise ValueError('runtime binary digest mismatch')
    s=job['strategy']
    if digest(s)!=job['strategy_sha256'] or s['dialect'] not in CLI_DIALECTS:
        raise ValueError('strategy binding mismatch')
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'strategy.json';path.write_text(json.dumps(s),encoding='utf-8')
        proc=subprocess.run([str(binary),'compile',str(path),'--dialect',CLI_DIALECTS[s['dialect']]],cwd=d,env={'PATH':os.defpath,'HOME':d,'LANG':'C.UTF-8','NO_COLOR':'1'},capture_output=True,timeout=30,check=True)
    if len(proc.stdout)>1_000_000:
        raise ValueError('oversized compiler output')
    compiled=json.loads(proc.stdout);validator.validate(compiled)
    if compiled['strategy_id']!=s['strategy_id'] or compiled['dialect']!=s['dialect']:
        raise ValueError('compiler result binding mismatch')
    held=compiled['review_required'] or bool(compiled['loss_codes']) or any(w['review_required'] for w in compiled['warnings']) or compiled['fidelity'] not in ('exact','source_equivalent')
    return {'strategy_id':s['strategy_id'],'strategy_sha256':job['strategy_sha256'],'runtime_sha256':pin,'qualification_receipt':qualification,'compiled':compiled,'status':'translation_review_required' if held else 'compiled_not_executed','execution_authorized':False}


def main():
    from jsonschema import Draft202012Validator
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('early','current','canary','schema-dir','output-dir'):
        p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--compiler',type=Path);p.add_argument('--compiler-sha256');p.add_argument('--qualification-receipt');a=p.parse_args()
    early=member(a.early,EARLY,'equator-article-survey.json');current=member(a.current,CURRENT,'equator-article-survey.json');recovery=member(a.canary,CANARY,'bibliographic-recovery.json')
    audit=gap_audit(early,current,recovery);plan=plan_searches(audit,recovery)
    schemas={k:read_pinned(a.schema_dir/(k+'.json'),v) for k,v in SCHEMA_PINS.items()}
    registry=schema_registry(schemas);validator=Draft202012Validator(schemas['strategy'],registry=registry)
    for job in plan['strategies']:validator.validate(job['strategy'])
    plan['schema_pins']=SCHEMA_PINS
    plan['compilations']=[]
    if a.compiler:
        cv=Draft202012Validator(schemas['compiled'],registry=registry);ids=set(plan['next_bounded_batch'])
        plan['compilations']=[compile_one(job,a.compiler,a.compiler_sha256,a.qualification_receipt,cv) for job in plan['strategies'] if job['strategy']['strategy_id'] in ids]
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for name,doc in [('persistent-gaps.json',audit),('searchright-strategies.json',plan)]:
        (a.output_dir/name).write_text(json.dumps(doc,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
