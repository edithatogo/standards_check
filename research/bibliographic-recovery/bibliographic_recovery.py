"""Read-only bibliographic recovery projection; catalogue identities are never merged."""
import argparse
import hashlib
import http.client
import json
import re
import time
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit, urlunsplit

PIN = '21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01'
DOI = re.compile(r'10\.\d{4,9}/[A-Za-z0-9._;()/:+<>\-]{1,220}', re.I)
PATTERNS = {'doi': DOI, 'pmid': re.compile(r'[1-9]\d{0,9}'), 'pmcid': re.compile(r'PMC[1-9]\d{0,9}'), 'openalex': re.compile(r'W[1-9]\d*')}


def ident(kind, value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if kind == 'doi':
        value = value.lower().removeprefix('https://doi.org/')
    elif kind == 'pmid':
        value = value.removeprefix('https://pubmed.ncbi.nlm.nih.gov/').strip('/')
    elif kind == 'pmcid':
        value = value.removeprefix('https://www.ncbi.nlm.nih.gov/pmc/articles/').removeprefix('https://pmc.ncbi.nlm.nih.gov/articles/').strip('/')
    elif kind == 'openalex':
        value = value.removeprefix('https://openalex.org/')
    return value if PATTERNS[kind].fullmatch(value) else None


def link_id(url):
    """Literal ID from an explicitly supported URL shape, not a fetched URL."""
    if not isinstance(url, str) or len(url) > 2048:
        return None
    try:
        u = urlsplit(url)
        if u.scheme not in ('http', 'https') or u.username or u.password or u.port is not None:
            return None
        host, path = u.hostname, unquote(u.path)
        if host in ('doi.org', 'dx.doi.org'):
            kind, value = 'doi', path.lstrip('/')
        elif host == 'pubmed.ncbi.nlm.nih.gov':
            kind, value = 'pmid', path.strip('/')
        elif host in ('www.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov') and path.startswith('/pubmed/'):
            kind, value = 'pmid', path.removeprefix('/pubmed/').strip('/')
        elif host in ('pmc.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov') and re.fullmatch(r'/(?:pmc/)?articles/PMC[1-9]\d*/?', path):
            kind, value = 'pmcid', path.strip('/').split('/')[-1]
        elif host == 'link.springer.com' and path.startswith('/article/'):
            kind, value = 'doi', path.removeprefix('/article/')
        elif host == 'journals.plos.org' and re.fullmatch(r'/plos[a-z]+/article(?:/file)?', path):
            values = parse_qs(u.query).get('id', [])
            kind, value = 'doi', values[0] if len(values) == 1 else ''
        else:
            return None
        value = ident(kind, value)
        return (kind, value) if value else None
    except ValueError:
        return None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def index(rows):
    result = {r['id']: r for r in rows}
    if len(result) != len(rows):
        raise ValueError('duplicate catalogue identity')
    return result


def plan(catalogue, source_links, survey):
    if len({x['source_revision'] for x in (catalogue, source_links, survey)}) != 1:
        raise ValueError('source revision mismatch')
    c, l, s = (index(x) for x in (catalogue['guidelines'], source_links['guidelines'], survey['records']))
    if not set(c) == set(l) == set(s):
        raise ValueError('catalogue denominator mismatch')
    providers = survey['provider_evidence']['records']
    rows, candidate_groups, work_groups = [], defaultdict(set), defaultdict(set)
    for key, cat in sorted(c.items()):
        lr, sr = l[key], s[key]
        if len({x['source_blob_sha'] for x in (cat, lr, sr)}) != 1:
            raise ValueError('source blob mismatch')
        values = defaultdict(set)
        for field, kind in (('doi','doi'),('pmid','pmid'),('resolved_doi','doi'),('resolved_pmid','pmid'),('pmcid','pmcid')):
            for obj in (cat, sr):
                v = ident(kind, obj.get(field))
                if v:
                    values[kind].add(v)
        provider = providers.get(key, {})
        oa = provider.get('openalex', {})
        cross = provider.get('crossref', {})
        if oa.get('status') == 'exact_identifier_metadata':
            for field, kind in (('resolved_doi','doi'),('resolved_pmid','pmid'),('openalex_id','openalex')):
                v = ident(kind, oa.get(field))
                if v:
                    values[kind].add(v)
        if cross.get('status') == 'exact_doi_metadata':
            v = ident('doi', cross.get('resolved_doi'))
            if v:
                values['doi'].add(v)
        conflict = bool(sr.get('provider_disagreements')) or any(len(v)>1 for v in values.values()) or any(x.get('status') == 'identifier_conflict' for x in (oa,cross))
        known = sorted(f'{k}:{v}' for k, vs in values.items() for v in vs)
        # Distinct source URLs may refer to co-publications, corrections or different versions.
        candidates = defaultdict(set)
        direct = []
        for lead in lr['candidates']:
            found = link_id(lead.get('url'))
            if found:
                token = ':'.join(found)
                candidates[token].update(safe_links([lead['url']]))
                candidate_groups[token].add(key)
            if lead.get('type') in ('source_file_candidate','interactive_page_candidate'):
                direct.extend(safe_links([lead['url']]))
        if not conflict:
            for token in known:
                work_groups[token].add(key)
        status = sr['status']
        route = ('identity_hold' if conflict else 'link_identifier_candidate' if status in ('missing_identifier','lookup_incomplete') and candidates else 'issuer_asset_candidate' if direct and status != 'oa_xml_candidate' else 'existing_identifier' if known else 'issuer_landing_candidate' if lr['candidates'] else 'title_discovery_candidate' if cat.get('title') else 'manual_identity_hold')
        rows.append({'id':key,'source_blob_sha':cat['source_blob_sha'],'title':cat.get('title'), 'status':status,'route':route,'publication_identity':known,'identity_conflict':conflict,'link_identifier_candidates':{k:sorted(v) for k,v in sorted(candidates.items())},'issuer_asset_candidates':sorted(set(direct)),'link_count':len(lr['candidates']),'crossref_status':cross.get('status'),'openalex_status':oa.get('status')})
    return {'source_revision':catalogue['source_revision'],'rows':rows,'route_counts':dict(Counter(r['route'] for r in rows)),'shared_link_candidates':{k:sorted(v) for k,v in sorted(candidate_groups.items()) if len(v)>1},'shared_metadata_identity_candidates':{k:sorted(v) for k,v in sorted(work_groups.items()) if len(v)>1},'canonical_packs_promoted':0,'boundary':'Candidates only. No primary-edition selection, rights inference, guideline deduplication or semantic equivalence.'}


def task_queue(receipt, previous=()):
    tasks = defaultdict(set)
    urgent = set()
    for r in receipt['rows']:
        if r['identity_conflict']:
            continue
        if r['route'] == 'link_identifier_candidate':
            for token in r['link_identifier_candidates']:
                kind,value=token.split(':',1)
                tasks[(kind,value)].add(r['id'])
                urgent.add((kind,value))
        elif r['route'] == 'title_discovery_candidate' and len(r['title']) <= 500:
            tasks[('title',r['title'])].add(r['id'])
            urgent.add(('title',r['title']))
        # Exact existing identifier enrichment, separate from link-only candidates.
        existing = [token.split(':',1) for token in r['publication_identity']]
        for kind in ('doi','pmid','pmcid'):
            matched = [tuple(t) for t in existing if t[0]==kind]
            if matched:
                for token in matched:
                    tasks[token].add(r['id'])
                break
    seen = set(previous)
    by_kind=defaultdict(list)
    for (kind,value),ids in sorted(tasks.items()):
        identity=digest([receipt['source_revision'],kind,value,sorted(ids)])
        if identity not in seen:
            by_kind[kind].append({'kind':kind,'value':value,'catalogue_ids':sorted(ids),'task_id':identity,'priority':'gap_candidate' if (kind,value) in urgent else 'identifier_enrichment'})
    # Gap candidates before enrichment, round-robin by route. Never rank by citations.
    order=[]
    for priority in ('gap_candidate','identifier_enrichment'):
        current={k:[t for t in v if t['priority']==priority] for k,v in by_kind.items()}
        while any(current.values()):
            for kind in ('doi','pmid','pmcid','title'):
                if current.get(kind):
                    order.append(current[kind].pop(0))
    return order


def select_tasks(receipt, budget, previous=()):
    if not 0 <= budget <= 12:
        raise ValueError('metadata request budget outside 0..12')
    return task_queue(receipt,previous)[:budget]


def orcid(value):
    if not isinstance(value,str):
        return None
    value=value.removeprefix('https://orcid.org/')
    if not re.fullmatch(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]',value):
        return None
    digits=value.replace('-','');total=0
    for d in digits[:-1]:
        total=(total+int(d))*2
    check=(12-total%11)%11
    return value if digits[-1]==('X' if check==10 else str(check)) else None


def count(value):
    return value if type(value) is int and value>=0 else None


def safe_links(values):
    """Locator hints only, strip query/credentials; never dereference."""
    out=set()
    for v in values:
        if not isinstance(v,str) or len(v)>2048:
            continue
        try:
            u=urlsplit(v)
            if u.scheme in ('http','https') and u.hostname and not (u.username or u.password):
                out.add(urlunsplit((u.scheme,u.netloc,u.path,'','')))
        except ValueError:
            continue
    return sorted(out)[:12]


def metadata(record, provider, requested):
    if provider not in ('crossref','openalex'):
        raise ValueError('unsupported provider')
    doi=ident('doi',record.get('DOI' if provider=='crossref' else 'doi'))
    if doi != requested:
        return {'status':'identifier_conflict','observed_doi':doi}
    if provider=='crossref':
        authors=[a.get('ORCID') for a in record.get('author',[]) if isinstance(a,dict)]
        refs=[ident('doi',r.get('DOI')) for r in record.get('reference',[]) if isinstance(r,dict)]
        relations=[{'type':k,'doi':v} for k,rs in (record.get('relation') or {}).items() for r in rs if isinstance(r,dict) and (v:=ident('doi',r.get('id')))]
        year=((record.get('published') or {}).get('date-parts') or [[None]])[0][0]
        cited,refcount=count(record.get('is-referenced-by-count')),count(record.get('reference-count'))
        extra={'relations':relations,'reference_dois':sorted({r for r in refs if r})[:250],'reference_dois_truncated':len({r for r in refs if r})>250,'updated_relation_count':len(record.get('update-to',[])), 'locator_hints':safe_links([r.get('URL') for r in record.get('link',[]) if isinstance(r,dict)]),'licence_hints':safe_links([r.get('URL') for r in record.get('license',[]) if isinstance(r,dict)])}
    else:
        ids=record.get('ids') or {}
        if ids.get('doi') and ident('doi',ids['doi'])!=doi:
            return {'status':'identifier_conflict','observed_doi':doi}
        authors=[(a.get('author') or {}).get('orcid') for a in record.get('authorships',[]) if isinstance(a,dict)]
        cited,refcount=count(record.get('cited_by_count')),count(record.get('referenced_works_count'))
        year=record.get('publication_year')
        extra={'openalex_id':ident('openalex',record.get('id')),'pmid':ident('pmid',ids.get('pmid')),'pmcid':ident('pmcid',ids.get('pmcid')),'is_retracted':record.get('is_retracted'),'reference_work_ids':sorted({v for r in record.get('referenced_works',[]) if (v:=ident('openalex',r))})[:250], 'locator_hints':safe_links([r.get(k) for r in record.get('locations',[]) if isinstance(r,dict) and r.get('is_oa') is True for k in ('landing_page_url','pdf_url')]), 'licence_hints':sorted({r['license'] for r in record.get('locations',[]) if isinstance(r,dict) and isinstance(r.get('license'),str)})[:12]}
    return {'status':'exact_doi_metadata','doi':doi,'cited_by_count':cited,'reference_count':refcount,'publication_year':count(year),'title':(record.get('title') or [''])[0] if provider=='crossref' else record.get('title'),'orcid_observations':sorted({v for r in authors if (v:=orcid(r))}),'orcid_authentication':'provider_assertion_not_locally_authenticated','rights':'metadata_only_not_reuse_permission',**extra}


def normal_title(text):
    return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',text).casefold())) if isinstance(text,str) else ''


def title_candidates(title, items):
    rows=[]
    for record in items[:3]:
        doi=ident('doi',record.get('DOI')); titles=record.get('title') or []
        text=titles[0] if titles else ''
        if doi:
            rows.append({'doi':doi,'title':text,'exact_normalized_title':bool(normal_title(title) and normal_title(title)==normal_title(text))})
    n=len({r['doi'] for r in rows if r['exact_normalized_title']})
    return {'status':'ambiguous_title_candidates' if n>1 else 'exact_title_candidate_unverified' if n==1 else 'no_exact_title_candidate','candidates':rows,'qualified_identity':False}


def observe(task, failures=None):
    """Reuse repository fixed-host, bounded, no-redirect fetch; no source downloads."""
    from scripts.source_provider_evidence import CROSSREF, EUROPE, OPENALEX, fetch
    kind,value=task['kind'],task['value'];out=[]
    failures = Counter() if failures is None else failures
    def request(provider,host,path,project):
        if failures[provider] >= 3:
            out.append({'provider':provider,'result':{'status':'deferred_circuit_breaker'}})
            return
        start=time.perf_counter()
        try:
            raw=fetch(host,path); data=json.loads(raw);result=project(data)
            failures[provider] = 0
            out.append({'provider':provider,'response_sha256':hashlib.sha256(raw).hexdigest(),'response_bytes':len(raw),'result':result,'seconds':time.perf_counter()-start})
        except (OSError,ValueError,KeyError,TypeError,IndexError,http.client.HTTPException) as exc:
            failures[provider] += 1
            out.append({'provider':provider,'result':{'status':'lookup_incomplete','error_type':type(exc).__name__},'seconds':time.perf_counter()-start})
        finally:
            time.sleep(1.0)
    if kind=='doi':
        request('crossref',CROSSREF,'/works/'+quote(value,safe=''),lambda d:metadata(d['message'],'crossref',value))
        request('openalex',OPENALEX,'/works/doi:'+quote(value,safe=''),lambda d:metadata(d,'openalex',value))
    elif kind=='title':
        request('crossref',CROSSREF,'/works?'+urlencode({'query.bibliographic':value,'rows':3,'select':'DOI,title,published'}),lambda d:title_candidates(value,d['message']['items']))
    else:
        field='EXT_ID' if kind=='pmid' else 'PMCID'
        query=('SRC:MED AND ' if kind=='pmid' else '')+field+':'+value
        def project(d):
            records=[]
            for r in d['resultList']['result'][:5]:
                match=ident(kind,r.get(kind))==value or kind=='pmid' and r.get('source')=='MED' and ident('pmid',r.get('id'))==value
                if match:
                    records.append({'doi':ident('doi',r.get('doi')),'pmid':ident('pmid',r.get('pmid') or r.get('id')),'pmcid':ident('pmcid',r.get('pmcid')),'cited_by_count':count(r.get('citedByCount')),'is_open_access':r.get('isOpenAccess')})
            return {'status':'exact_identifier_candidates' if records else 'no_exact_identifier_observed','candidates':records,'rights':'unassessed'}
        request('europe_pmc',EUROPE,'/europepmc/webservices/rest/search?'+urlencode({'query':query,'format':'json','pageSize':5}),project)
    return {**task,'observations':out,'observed_at':datetime.now(timezone.utc).isoformat(),'qualified_identity':False}


def run(archive,budget=0,previous=()):
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=PIN:
        raise ValueError('unverified census archive')
    with zipfile.ZipFile(archive) as z:
        c,l,s=[json.loads(z.read(n)) for n in ('equator-catalogue.json','equator-source-link-candidates.json','equator-article-survey.json')]
    result=plan(c,l,s);result['archive_sha256']=PIN
    result['remaining_task_count']=len(task_queue(result,previous))
    result['task_plan']=select_tasks(result,budget,previous)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--budget',type=int,default=0);p.add_argument('--live',action='store_true');p.add_argument('--previous',type=Path);p.add_argument('--previous-sha256');a=p.parse_args()
    previous=[]
    if a.previous:
        raw=a.previous.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=a.previous_sha256:
            raise ValueError('previous receipt hash mismatch')
        prior=json.loads(raw)
        if prior.get('archive_sha256')!=PIN:
            raise ValueError('previous receipt input mismatch')
        previous=sorted(set(prior.get('attempted_task_ids',[]))|{r['task_id'] for r in prior.get('observations',[]) if any(o['result']['status']!='deferred_circuit_breaker' for o in r['observations'])})
    result=run(a.archive,a.budget,previous)
    failures=Counter()
    result['observations']=[observe(t, failures) for t in result['task_plan']] if a.live else []
    result['attempted_task_ids']=sorted(set(previous)|{r['task_id'] for r in result['observations'] if any(o['result']['status']!='deferred_circuit_breaker' for o in r['observations'])})
    result['live_attempted']=a.live
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
