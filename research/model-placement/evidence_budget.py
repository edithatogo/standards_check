"""Equal candidate-budget evidence escalation replay; no new inference."""
import argparse
import json
import math
import random
import resource
import statistics
import time
from pathlib import Path
from replay import load, fuse, select


def expand(first, full, chosen, *, extra=5):
    if set(first) != set(full) or not chosen <= set(first) or extra < 0:
        raise ValueError('query coverage or budget mismatch')
    out = {}
    for k, order in first.items():
        if len(set(order)) != len(order) or len(set(full[k])) != len(full[k]) or not set(order) <= set(full[k]):
            raise ValueError('candidate universe mismatch')
        added = [c for c in full[k] if c not in order][:extra] if k in chosen else []
        if k in chosen and len(added) != extra:
            raise ValueError('insufficient expansion candidates')
        out[k] = order + added
    return out


def allocation(ids, priority, percent):
    if set(ids) != set(priority) or not 0 <= percent <= 100 or any(not math.isfinite(v) for v in priority.values()):
        raise ValueError('invalid priority ledger')
    chosen = set()
    for instrument in sorted({k[0] for k in ids}):
        group = [k for k in ids if k[0] == instrument]
        chosen |= select(group, lambda k: priority[k], len(group)*percent//100)
    return chosen


def gains(refs, before, after):
    if set(refs) != set(before) or set(refs) != set(after):
        raise ValueError('query mismatch')
    gain = sum(len((set(after[k])-set(before[k])) & refs[k]) for k in refs)
    loss = sum(len((set(before[k])-set(after[k])) & refs[k]) for k in refs)
    return gain,loss


def run(root):
    started=time.perf_counter()
    prior=load(root,15088716936,'paired.json')['results']; qwen=load(root,15091588651,'report.json')
    key=lambda r:(r['instrument_id'],r['item_id'])
    bge={key(r):r['ranking'] for r in prior['bge']['rows']}; char={key(r):r['ranking'] for r in prior['char']['rows']}
    refs={key(r):set(r['reference']) for r in prior['bge']['rows']}; scores={key(r):r['scores'] for r in qwen['provider_rows']}
    if not set(bge)==set(char)==set(refs)==set(scores) or any(set(scores[k])!=set(bge[k][:10]) or any(not math.isfinite(v) for v in scores[k].values()) for k in bge):
        raise ValueError('incompatible receipts')
    ids=sorted(bge); groups={i:[k for k in ids if k[0]==i] for i in sorted({k[0] for k in ids})}; first={k:bge[k][:5] for k in ids}; full={k:fuse(bge[k],char[k]) for k in ids}
    score_order={k:sorted((scores[k][c] for c in first[k]),reverse=True) for k in ids}
    priorities={'fixed':{k:0 for k in ids},'low_max':{k:-score_order[k][0] for k in ids},'small_gap':{k:-(score_order[k][0]-score_order[k][1]) for k in ids},'lexical_disagreement':{k:-len(set(first[k])&set(char[k][:5])) for k in ids}}
    total=sum(map(len,refs.values())); initial=sum(len(set(first[k])&refs[k]) for k in ids); results={}
    eligible_gains={k:len((set([c for c in full[k] if c not in first[k]][:5]))&refs[k]) for k in ids}
    for budget in (25,50,75,100):
        arms={}; fixed=allocation(ids,priorities['fixed'],budget)
        for name,priority in priorities.items():
            chosen=allocation(ids,priority,budget); order=expand(first,full,chosen); gain,loss=gains(refs,first,order)
            arms[name]={'queries_expanded':len(chosen),'candidates':sum(map(len,order.values())),'gains':gain,'losses':loss,'hits':initial+gain-loss,'misses':total-initial-gain+loss,'selected':[list(k) for k in sorted(chosen)],'by_instrument':{i:{'expanded':sum(k in chosen for k in group),'gains':sum(eligible_gains[k] for k in group if k in chosen)} for i,group in groups.items()}}
            if len(chosen)!=len(fixed):raise ValueError('unequal candidate budget')
        # Same number per instrument. Random baseline uses 1000 predeclared seeds.
        draws=[]
        for seed in range(1000):
            rng=random.Random(seed); chosen={k for group in groups.values() for k in rng.sample(group,len(group)*budget//100)}
            draws.append(sum(eligible_gains[k] for k in chosen))
        draws.sort(); expected=sum(sum(eligible_gains[k] for k in group)*(len(group)*budget//100)/len(group) for group in groups.values())
        results[str(budget)]={'arms':arms,'random':{'draws':1000,'mean_gains':statistics.mean(draws),'exact_expected_gains':expected,'q025':draws[25],'q975':draws[974],'minimum':draws[0],'maximum':draws[-1],'low_max_at_least_as_good_fraction':sum(x>=arms['low_max']['gains'] for x in draws)/1000}}
    return {'protocol':'equal-budget-evidence-escalation-replay-v1','scientific_qualification':False,'semantic_merges':0,'model_download_bytes':0,'fresh_inference':False,'reference_status':'editorial positive associations only; unlisted associations not known negatives','initial_hits':initial,'total_positive_associations':total,'budgets':results,'wall_seconds':time.perf_counter()-started,'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--artifacts',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.write_text(json.dumps(run(args.artifacts),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
