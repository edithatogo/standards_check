"""Measure the retained legacy metadata canary without claiming source admission."""
import argparse
import hashlib
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

PINS = {
    'census': '21046589502f064d54800c9f495d72d18b97184a1db376f06da773b84bde3f01',
    'canary': 'c409624a581a6d637e4ef19cca41ec5c82c6877ee1054b9750289158771627e1',
}
SUCCESS = {'exact_doi_metadata', 'exact_identifier_candidates'}


def index(rows):
    result = {row['id']: row for row in rows}
    if len(result) != len(rows):
        raise ValueError('duplicate catalogue identity')
    return result


def aggregate(records):
    successes = [r for r in records if r['status'] in SUCCESS]
    works = {w for r in successes for w in r['work_ids']}
    ids = {i for r in successes for i in r['ids']}
    seconds = sum(r['seconds'] for r in records if r['seconds'] is not None)
    return {'requests': len(records), 'exact_responses': len(successes),
            'unique_work_ids': len(works), 'work_ids': sorted(works),
            'catalogue_ids_with_exact_response': len(ids), 'catalogue_ids': sorted(ids),
            'status_counts': dict(Counter(r['status'] for r in records)),
            'observed_request_seconds': seconds,
            'requests_timed': sum(r['seconds'] is not None for r in records),
            'response_bytes_observed': sum(r['response_bytes'] for r in records if r['response_bytes'] is not None),
            'responses_with_byte_count': sum(r['response_bytes'] is not None for r in records),
            'seconds_per_distinct_work_lead': seconds/len(works) if works and all(r['seconds'] is not None for r in records) else None,
            'qualified_editions': 0}


def exact_works(kind, value, result):
    status = result['status']
    if status not in SUCCESS:
        return []
    if status == 'exact_doi_metadata':
        if kind != 'doi' or result.get('doi') != value:
            raise ValueError('exact DOI identity mismatch')
        return ['doi:'+value]
    if kind not in ('pmid','pmcid') or not result.get('candidates'):
        raise ValueError('exact identifier identity mismatch')
    works = set()
    for row in result['candidates']:
        if row.get(kind) != value:
            raise ValueError('exact identifier identity mismatch')
        # Prefer DOI where present; preserve alternate identifier namespaces.
        for name in ('doi','pmid','pmcid'):
            if row.get(name):
                works.add(name+':'+row[name])
                break
    if len(works) != 1:
        raise ValueError('ambiguous exact identifier work')
    return sorted(works)


def age_band(year):
    if type(year) is not int or not 1900 <= year <= 2026:
        return 'unknown'
    age = 2026-year
    return '0-4' if age <= 4 else '5-9' if age <= 9 else '10+'


def report(catalogue, receipt):
    c,r = index(catalogue['guidelines']),index(receipt['rows'])
    if catalogue['source_revision'] != receipt['source_revision'] or set(c) != set(r) or any(c[k]['source_blob_sha'] != r[k]['source_blob_sha'] for k in c):
        raise ValueError('catalogue identity binding mismatch')
    rows = []
    seen = set()
    for task in receipt['observations']:
        kind,value,ids = task['kind'],task['value'],task['catalogue_ids']
        if not ids or len(ids)!=len(set(ids)) or not set(ids)<=set(c):
            raise ValueError('invalid task catalogue identity')
        for obs in task['observations']:
            result=obs['result'];key=(obs['provider'],kind,value)
            if key in seen:
                raise ValueError('duplicate provider-query attempt')
            seen.add(key)
            if result['status']=='deferred_circuit_breaker':
                continue
            seconds,byte_count=obs.get('seconds'),obs.get('response_bytes')
            if seconds is not None and (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<0):
                raise ValueError('invalid resource receipt')
            if byte_count is not None and (type(byte_count) is not int or byte_count<0):
                raise ValueError('invalid byte receipt')
            rows.append({'provider':obs['provider'],'kind':kind,'value':value,'ids':ids,'status':result['status'],
                         'seconds':seconds,'response_bytes':byte_count,'work_ids':exact_works(kind,value,result),
                         'publication_age_band':age_band(result.get('publication_year')),
                         'source_routes':sorted({r[k]['route'] for k in ids}),
                         'study_types':sorted({t for k in ids for t in c[k].get('study_types',[])}) or ['unknown'],
                         'family_proxies':sorted({c[k].get('acronym') or k for k in ids})})
    def strata(field):
        groups=defaultdict(list)
        for row in rows:
            v=row[field]
            for name in v if isinstance(v,list) else [v]:
                groups[name].append(row)
        return {k:aggregate(v) for k,v in sorted(groups.items())}
    return {'protocol':'historical-legacy-metadata-yield-v1','reference_year':2026,'source_revision':receipt['source_revision'],
            'overall':aggregate(rows),'by_provider':strata('provider'),'by_query_type':strata('kind'),
            'by_source_route':strata('source_routes'),'by_age':strata('publication_age_band'),
            'by_study_type':strata('study_types'),'by_family_proxy':strata('family_proxies'),'rows':rows,
            'boundary':'Retained selected legacy metadata requests only; not native Searchright, a matched-provider benchmark, or source qualification. Work IDs are preferred observed identifiers, not fuzzy deduplication. Age unknown without observed year; family proxies and overlapping source/study strata are descriptive. Request seconds exclude spacing, setup and document acquisition; missing bytes are not zero. No independent labels or paid cost inferred.'}


def member(path,pin,name):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:
        raise ValueError('archive digest mismatch')
    with zipfile.ZipFile(path) as z:
        return json.loads(z.read(name))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--census',type=Path,required=True);p.add_argument('--canary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=report(member(a.census,PINS['census'],'equator-catalogue.json'),member(a.canary,PINS['canary'],'bibliographic-recovery.json'))
    result['artifact_pins']=PINS
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
