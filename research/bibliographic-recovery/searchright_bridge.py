"""Read-only consumer of pinned Searchright source descriptions and work contract."""
import argparse
import hashlib
import json
from pathlib import Path

from bibliographic_recovery import digest, ident, safe_links

PINS = {
    'policies': '64c1e0a146d9c18026be60a21ada1f2d01aa5b95',
    'methods': '075be1a81dfb1a5422a5fe74dc7ce1be88f5224a',
    'advisory': 'b921ed181a59a4eadeb5eb244e159f8556f6c679',
    'directories': '7906bd6996e523d474650039ed5ed34dfba1dbbf',
    'schema': '26f48879eb9401e0e41bc4cfb9d00e6a378f9f47',
}
REVISION = '444c5199c0887c0259fe47c3d2545b5c6b877d6d'
ADVISORY_REVISION = '703f9ede74d78ac3aa58ee322c48471875f2a80e'


def read_pinned(path, pin):
    raw = path.read_bytes()
    # Git SHA-1 is checked for upstream blob identity, not security authentication.
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw, usedforsecurity=False).hexdigest() != pin:
        raise ValueError('Searchright blob mismatch')
    return json.loads(raw)


def crosswalk(inputs):
    sources = [
        ('policies', inputs['policies']['providers'], 'provider_id'),
        ('methods', inputs['methods'], 'source_id'),
        ('advisory', inputs['advisory']['sources'], 'source_id'),
        ('directories', inputs['directories']['directories'], 'directory_id'),
    ]
    rows = []
    for surface, records, field in sources:
        seen = set()
        for r in records:
            key = r[field]
            if not key or key in seen:
                raise ValueError('duplicate or empty source identity')
            seen.add(key)
            if surface == 'policies':
                route = 'existing_standardflow_metadata_adapter' if key in {'crossref', 'openalex', 'europe-pmc'} else 'pubmed_identity_candidate'
            elif surface == 'directories':
                route = 'advisory_directory_only'
            elif surface == 'methods':
                route = {'repository':'supplement_or_issuer_asset_candidate', 'grey_literature':'issuer_or_publication_discovery', 'forward_citation':'citation_graph_fixture_only', 'backward_citation':'reference_candidate_discovery', 'trial_registry':'development_study_linkage_only'}.get(r['method'], 'documented_manual_method')
            else:
                route = 'assess_source_platform_and_authorized_exports'
            rows.append({'surface':surface, 'source_id':key, 'route':route, 'access':r.get('access_class',r.get('access_mode',r.get('access_characterization'))), 'platforms':r.get('platforms',[]), 'review_due':r.get('review_due'), 'policy_status':r.get('policy_review_status'), 'execution_authorized':False})
    return rows


def project_records(receipt):
    """Never pretend a catalogue title or a link hint is a provider work record."""
    rows = []
    seen = set()
    for task in receipt['observations']:
        if task['kind'] != 'doi':
            continue
        for obs in task['observations']:
            r = obs['result']
            doi = ident('doi',r.get('doi'))
            if r['status'] != 'exact_doi_metadata' or not doi or doi != task['value'] or not isinstance(r.get('title'),str) or not r['title'].strip():
                continue
            key = digest([task['task_id'],obs['provider'],obs['response_sha256']])
            if key in seen:
                raise ValueError('duplicate provider observation')
            seen.add(key)
            year = r.get('publication_year')
            rows.append({'schema_version':'org.searchright.bibliographic-record.v1','record_id':key,'source_receipt_id':obs['response_sha256'],'native_id':obs['provider']+':doi:'+doi,'kind':{'other':'unqualified_work_candidate'},'identifiers':{'doi':doi,'pmid':ident('pmid',r.get('pmid')),'pmcid':ident('pmcid',r.get('pmcid')),'openalex':ident('openalex',r.get('openalex_id')),'other':{}},'title':r['title'],'abstract_text':None,'authors':[],'container_title':None,'publication_year':year if type(year) is int and 0<=year<=30000 else None,'publication_date':None,'languages':[],'subjects':[],'urls':safe_links(['https://doi.org/'+doi]+r.get('locator_hints',[])),'provider_metadata':{'catalogue_ids':task['catalogue_ids'],'task_id':task['task_id'],'observed_at':task['observed_at'],'provider':obs['provider'],'edition_qualified':False,'observation':r}})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    inputs={k:read_pinned(a.source_dir/(k+'.json'),v) for k,v in PINS.items()}
    rows=crosswalk(inputs)
    records=project_records(json.loads(a.receipt.read_bytes()))
    # Use the actual upstream wire contract; it does not confer runtime or rights qualification.
    from jsonschema import Draft202012Validator
    validator=Draft202012Validator(inputs['schema'])
    for record in records:
        validator.validate(record)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    result={'searchright_revision':REVISION,'advisory_pr844_revision':ADVISORY_REVISION,'source_blob_pins':PINS,'source_rows':rows,'records_exported':len(records),'dedup_execution':'held_upstream_security_and_privacy','scientific_qualification':False,'canonical_packs_promoted':0,'boundary':'Source, method and advisory directory rows overlap; not live provider counts. PR #844 is unmerged. No automatic identity or guideline merge.'}
    for name,data in [('searchright-crosswalk.json',result),('searchright-records.json',records)]:
        (a.output_dir/name).write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':main()
