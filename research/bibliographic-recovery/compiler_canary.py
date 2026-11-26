"""Offline feasibility probe of the pinned native CLI, never runtime admission."""
import argparse
import hashlib
import json
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path

DIALECTS = {'crossref':'crossref','open_alex':'openalex','pub_med':'pubmed','europe_pmc':'europe-pmc'}
REVISION = '444c5199c0887c0259fe47c3d2545b5c6b877d6d'
TREE = '0929bd9b17b81d98f8b59cca2d41367f8f95aafc'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def assess(job, compiled):
    strategy = job['strategy']
    if compiled['strategy_id'] != strategy['strategy_id'] or compiled['dialect'] != strategy['dialect']:
        raise ValueError('compiler result binding mismatch')
    held = (compiled['review_required'] or bool(compiled['loss_codes'])
            or any(w['review_required'] for w in compiled['warnings'])
            or compiled['fidelity'] not in ('exact','source_equivalent'))
    return {'strategy_id':strategy['strategy_id'],'compiled':compiled,
            'status':'translation_review_required' if held else 'compiled_candidate_not_admitted',
            'runtime_qualified':False,'execution_authorized':False}


def selected_jobs(plan):
    if plan['mechanism']!='searchright' or plan['execution_status']!='held_runtime_qualification':
        raise ValueError('expected held native plan')
    jobs=plan['strategies']; indexed={x['strategy']['strategy_id']:x for x in jobs}; batch=plan['next_bounded_batch']
    if len(indexed)!=len(jobs) or not 0<len(batch)<=8 or len(set(batch))!=len(batch) or not set(batch)<=set(indexed):
        raise ValueError('invalid batch')
    selected=[indexed[k] for k in batch]
    if any(x['execution_authorized'] is not False for x in selected):
        raise ValueError('execution authorization is prohibited in this probe')
    return selected


def run(plan, binary, pin, validator, host_netns):
    if os.readlink('/proc/self/ns/net')==host_netns or os.geteuid()==0:
        raise ValueError('unprivileged isolated network namespace required')
    # No non-loopback interface in the disposable namespace. Never fall back to host network.
    if any(line.split(':',1)[0].strip()!='lo' for line in Path('/proc/net/dev').read_text().splitlines()[2:] if ':' in line):
        raise ValueError('isolated namespace has network interface')
    binary=binary.resolve(strict=True)
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=pin:
        raise ValueError('binary digest mismatch')
    if plan.get('searchright_revision')!=REVISION:
        raise ValueError('upstream revision mismatch')
    results=[]
    for job in selected_jobs(plan):
        strategy=job['strategy']; start=time.perf_counter()
        if digest(strategy)!=job['strategy_sha256'] or strategy['dialect'] not in DIALECTS:
            raise ValueError('strategy digest or dialect mismatch')
        out={'strategy_id':strategy['strategy_id'],'strategy_sha256':job['strategy_sha256'],
             'runtime_qualified':False,'execution_authorized':False}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'strategy.json';path.write_text(json.dumps(strategy),encoding='utf-8')
            try:
                p=subprocess.run([str(binary),'compile',str(path),'--dialect',DIALECTS[strategy['dialect']]],cwd=directory,env={'PATH':os.defpath,'HOME':directory,'LANG':'C.UTF-8','NO_COLOR':'1'},capture_output=True,timeout=30,check=False)
                out['returncode']=p.returncode
                out['stderr_sha256']=hashlib.sha256(p.stderr).hexdigest()
                if p.returncode:
                    out['status']='compiler_failed'
                else:
                    if len(p.stdout)>1_000_000:
                        raise ValueError('oversized compiler output')
                    compiled=json.loads(p.stdout);validator.validate(compiled)
                    out.update(assess(job,compiled));out['stdout_sha256']=hashlib.sha256(p.stdout).hexdigest()
            except Exception as exc:
                out.update(status='compiler_probe_failed',error_type=type(exc).__name__)
        out['seconds']=time.perf_counter()-start;results.append(out)
    return {'protocol':'native-compiler-feasibility-v1','upstream_revision':REVISION,'upstream_tree':TREE,
            'binary_sha256':pin,'binary_bytes':binary.stat().st_size,'isolated_network':True,'runtime_qualified':False,
            'execution_authorized':False,'live_searches':0,'compilations':results,
            'peak_children_rss_kib_linux':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'boundary':'Candidate CLI compilation only; not a security-qualified runtime or authorized live host.'}


def main():
    from jsonschema import Draft202012Validator
    from searchright_recovery import SCHEMA_PINS, schema_registry
    from searchright_bridge import read_pinned
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','binary','schema-dir','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--binary-sha256',required=True);p.add_argument('--host-netns',required=True);a=p.parse_args()
    schemas={k:read_pinned(a.schema_dir/(k+'.json'),v) for k,v in SCHEMA_PINS.items()}
    validator=Draft202012Validator(schemas['compiled'],registry=schema_registry(schemas))
    result=run(json.loads(a.plan.read_bytes()),a.binary,a.binary_sha256,validator,a.host_netns)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    if any(x['status'] not in ('compiled_candidate_not_admitted','translation_review_required') for x in result['compilations']):
        raise SystemExit('one or more compiler cases failed; receipt retained')


if __name__=='__main__':main()
