"""Opt-in author-labelled synthetic placement controls; no guideline source wording.
Two development families, four untouched evaluation families. No canonical writes.
"""
import argparse
import hashlib
import json
import math
import re
import resource
import time
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

ROLES = ('actor', 'condition', 'exception')
FAMILIES = {
    'PRISMA': (['Review authors','Screening staff'], ['when screening records','if resolving duplicates'], ['except pilot records','unless records are withdrawn'], ['record database names','record search dates','record exclusions'], ['list database names','list search dates','list exclusions']),
    'CHEERS': (['Analysts','Study economists'], ['when estimating costs','if projecting outcomes'], ['except training cases','unless values are unavailable'], ['record price year','record time horizon','record discount rates'], ['list price year','list time horizon','list discount rates']),
    'CONSORT': (['Trial staff','Study coordinators'], ['when allocating groups','during follow-up'], ['except practice sessions','excluding withdrawn participants'], ['record treatment codes','record adverse events','record withdrawals'], ['list treatment codes','list adverse events','list withdrawals']),
    'STARD': (['Test assessors','Laboratory staff'], ['when reading tests','for repeat specimens'], ['except invalid samples','unless tests are incomplete'], ['record test thresholds','record reference results','record test dates'], ['list test thresholds','list reference results','list test dates']),
    'ARRIVE': (['Animal carers','Research staff'], ['if housing animals','during monitoring'], ['except acclimatisation days','excluding pilot animals'], ['record cage size','record diet type','record monitoring dates'], ['list cage size','list diet type','list monitoring dates']),
    'TRIPOD': (['Model developers','Validation staff'], ['when training models','for external validation'], ['except test records','unless data are missing'], ['record predictor definitions','record calibration estimates','record cohort dates'], ['list predictor definitions','list calibration estimates','list cohort dates']),
}


def fixture():
    rows = []
    for family, (actors, conditions, exceptions, actions, paraphrases) in FAMILIES.items():
        for i in range(6):
            # Paired near-neighbours share action but differ in independently authored qualifiers.
            a, c, e = actors[i % 2], conditions[(i//2 + i) % 2], exceptions[(i//3 + i) % 2]
            action, paraphrase = actions[i//2], paraphrases[i//2]
            rows.append(dict(id=f'{family}-{i+1}', family=family, split='dev' if family in ('PRISMA','CHEERS') else 'test', actor=a, condition=c, exception=e, action=action, heading=f'section-{i//2+1}', doc=f'{a} must {action} {c}, {e}.', query=f'{c}, {a} must {paraphrase}, {e}.'))
    return rows


def spans(row, side):
    return {role:(row[side].index(row[role]), row[side].index(row[role])+len(row[role])) for role in ROLES}


def verify_anchor(text, a, b, claim):
    return 0 <= a < b <= len(text) and text[a:b] == claim


def tokens(text):
    return list(re.finditer(r'\w+(?:-\w+)*|[^\w\s]',text))


def token_features(ts, i):
    w=ts[i].group(); prev=ts[i-1].group().lower() if i else '<start>'; nxt=ts[i+1].group().lower() if i+1<len(ts) else '<end>'
    return {'word':w.lower(), 'prev':prev, 'next':nxt,'upper':w[0].isupper(),'suffix':w[-3:].lower(),'start':i==0,'position':i/len(ts),'after_must':any(t.group()=='must' for t in ts[:i]),'before_comma':nxt==',','punct':not w[0].isalnum()}


def rule_tags(text):
    out={}
    for role, pattern in {'actor':r'\b([A-Z][a-z]+(?: [a-z]+)?) must\b','condition':r'\b((?:when|if) [^,.]+)','exception':r'\b((?:except|unless) [^,.]+)'}.items():
        m=re.search(pattern,text)
        if m: out[role]=m.span(1)
    return out


def fit_tagger(rows):
    x,y=[],[]
    for row in rows:
        if row['split']!='dev': continue
        for side in ('doc','query'):
            ts=tokens(row[side]); gold=spans(row,side)
            for i,t in enumerate(ts):
                x.append(token_features(ts,i)); y.append(next((r for r,(a,b) in gold.items() if a<=t.start() and t.end()<=b),'other'))
    vec=DictVectorizer(); model=LogisticRegression(max_iter=500, random_state=0,class_weight='balanced').fit(vec.fit_transform(x),y)
    def predict(text):
        ts=tokens(text); labels=model.predict(vec.transform([token_features(ts,i) for i in range(len(ts))])); out={}
        for role in ROLES:
            indices=[i for i,label in enumerate(labels) if label==role]
            # Abstain on discontiguous or missing predictions rather than fabricate a span.
            if indices and indices==list(range(indices[0],indices[-1]+1)):
                out[role]=(ts[indices[0]].start(),ts[indices[-1]].end())
        return out
    return predict


def span_counts(rows, tag):
    counts={r:[0,0,0] for r in ROLES}
    records=[]
    for row in rows:
        for side in ('doc','query'):
            predicted=tag(row[side]); expected=spans(row,side)
            for role in ROLES:
                counts[role][0]+=predicted.get(role)==expected[role]
                counts[role][1]+=role in predicted and predicted[role]!=expected[role]
                counts[role][2]+=predicted.get(role)!=expected[role]
            records.append({'id':row['id'],'side':side,'expected':expected,'predicted':predicted})
    return {'by_role':{r:{'tp':t,'fp':f,'fn':n,'precision':t/(t+f) if t+f else 0,'recall':t/(t+n),'f1':2*t/(2*t+f+n) if 2*t+f+n else 0} for r,(t,f,n) in counts.items()},'records':records}


def rrf(*orders):
    s=defaultdict(float)
    for order in orders:
        if len(set(order))!=len(order): raise ValueError('duplicate candidate')
        for i,k in enumerate(order,1): s[k]+=1/(60+i)
    return sorted(s,key=lambda k:(-s[k],k))


def overlap(a,b):
    a=set(re.findall(r'\w+',a.lower())); b=set(re.findall(r'\w+',b.lower()))
    return len(a&b)/max(1,len(a|b))


def role_text(text,tags,role):
    return text[slice(*tags[role])] if role in tags else ''


def layout(rows, root):
    import fitz
    import pdfplumber
    from reportlab.pdfgen.canvas import Canvas
    from textwrap import wrap
    path=root/'synthetic-layout.pdf'; c=Canvas(str(path),pagesize=(792,612),invariant=1)
    expected=[]
    for family in FAMILIES:
        items=[r for r in rows if r['family']==family]; page=[]
        c.setFont('Helvetica-Bold',13);c.drawString(32,582,f'{family} — synthetic controls only')
        for i,row in enumerate(items):
            x=32+380*(i//3); y=550-85*(i%3); item=f'{i//2+1}{"a" if i%2==0 else "b"}'; marker=f'[F{i+1}]'
            body=f'{item} {row["actor"]} must {row["action"]} {row["condition"]} {marker}'
            note=f'{marker} {row["exception"]}'
            c.rect(x,y-70,350,70);c.setFont('Helvetica',10)
            for j,line in enumerate(wrap(body,width=52)):c.drawString(x+7,y-17-13*j,line)
            ny=240-24*(i%3);c.rect(x,ny-20,350,20);c.drawString(x+7,ny-13,note)
            page.append(dict(id=row['id'],nested_id=item,body=body,note=note,page=len(expected)+1,body_region=[x,612-y,x+350,612-y+70],note_region=[x,612-ny,x+350,612-ny+20]))
        expected.append(page);c.showPage()
    c.save(); norm=lambda t:' '.join(t.split()); result={a:[] for a in ('pdfplumber_incumbent','fitz_whole','fitz_targeted')}
    with pdfplumber.open(path) as pdf, fitz.open(path) as doc:
        for index,page in enumerate(doc):
            cells=[]
            for drawing in page.get_drawings():
                for item in drawing['items']:
                    if item[0]=='re':
                        rect=item[1]; cells.append((norm(page.get_text(clip=rect)),list(rect)))
            arms={'pdfplumber_incumbent':[(norm(pdf.pages[index].extract_text() or ''),None)],'fitz_whole':[(norm(page.get_text(sort=True)),None)],'fitz_targeted':cells}
            for name,chunks in arms.items():
                for ref in expected[index]:
                    body=[box for txt,box in chunks if norm(ref['body']) in txt]; foot=[box for txt,box in chunks if norm(ref['note']) in txt]
                    result[name].append({'id':ref['id'],'page':index+1,'body':bool(body),'footnote':bool(foot),'body_and_note_present':bool(body and foot),'body_regions':body,'footnote_regions':foot})
        doc[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(root/'layout-page-1.png')
    return {'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'qualifier_linkage_measured':False,'reference':expected,'arms':{a:{'rows':len(rs),'complete_nested_rows':sum(r['body'] for r in rs),'footnotes':sum(r['footnote'] for r in rs),'co_extracted_body_note_pairs':sum(r['body_and_note_present'] for r in rs),'records':rs} for a,rs in result.items()}}


def pipeline(rows, tag):
    # Fixed development-only vectorizer and low-dimensional LSA; no transformer weights.
    dev=[r for r in rows if r['split']=='dev']; docs=[r[s] for r in dev for s in ('doc','query')]
    vec=TfidfVectorizer(analyzer='char',ngram_range=(2,4)).fit(docs); svd=TruncatedSVD(n_components=8,random_state=0).fit(vec.transform(docs))
    tag_cache={(r['id'],s):tag(r[s]) for r in rows for s in ('doc','query')}
    features={}; facets={}; by_family={}
    for family in FAMILIES:
        group=[r for r in rows if r['family']==family]; ids=[r['id'] for r in group]; q=[r['query'] for r in group]; d=[r['doc'] for r in group]
        lexical=cosine_similarity(vec.transform(q),vec.transform(d)); dense=cosine_similarity(svd.transform(vec.transform(q)),svd.transform(vec.transform(d)))
        for i,a in enumerate(group):
            for j,b in enumerate(group):
                at=tag_cache[a['id'],'query']; bt=tag_cache[b['id'],'doc']
                sim=[overlap(role_text(a['query'],at,r),role_text(b['doc'],bt,r)) for r in ROLES]
                features[a['id'],b['id']]=[float(lexical[i,j]),float(dense[i,j]),overlap(a['query'],b['doc']),*sim]
                facets[a['id'],b['id']]=[int(a[r]==b[r]) for r in ROLES]+[int(a['action']==b['action'])]
        by_family[family]=(group,ids,lexical,dense)
    training=[(a,b) for a,b in features if a.split('-')[0] in ('PRISMA','CHEERS')]
    x=[features[k] for k in training]; y=[int(a==b) for a,b in training]
    def fit(y):return LogisticRegression(random_state=0,class_weight='balanced',max_iter=500).fit(x,y)
    ranker=fit(y); atomic=[fit([facets[k][i] for k in training]) for i in range(4)]
    results={}; records=[]; decision_records=[]; step_records=[]
    for family,(group,ids,lexical,dense) in by_family.items():
        order=lambda s:sorted(range(len(ids)),key=lambda j:(-float(s[j]),ids[j])); graph=np.zeros((len(ids),len(ids)))
        # Graph derives from synthetic section hierarchy and adjacent dependency links, never gold matches.
        for i,a in enumerate(group):
            for j,b in enumerate(group):
                if i!=j:graph[i,j]=float(a['heading']==b['heading'])+.5*float(abs(i-j)==1)
        graph=graph/np.maximum(1,graph.sum(axis=1,keepdims=True)); fam=[]
        for i,a in enumerate(group):
            lex=lexical[i]; ds=dense[i]; seed=np.maximum(lex,0); seed=seed/max(1e-12,seed.sum())
            one=.7*seed+.3*seed@graph; diffusion=seed.copy()
            for _ in range(8):diffusion=.7*seed+.3*diffusion@graph
            tag_scores=np.array([sum(features[a['id'],b['id']][3:])/3 for b in group]); enriched=lex+.25*tag_scores
            lp=order(lex); dp=order(ds); fused=rrf(lp,dp); gp=order(one); mp=order(diffusion); combined=order(enriched+.25*diffusion)
            probs=ranker.predict_proba([features[a['id'],b['id']] for b in group])[:,1]
            # Same trained pointwise ranker and exactly three candidates per pool.
            ranked={'lexical':lp[:3],'dense':dp[:3],'fused':fused[:3],'tag_enriched':order(enriched)[:3],'graph_simple':gp[:3],'graph_diffusion':mp[:3],'graph_simple_rerank':sorted(lp[:3],key=lambda j:(-one[j],ids[j])),'graph_feature_rerank':sorted(lp[:3],key=lambda j:(-diffusion[j],ids[j])),'learned_lexical':sorted(lp[:3],key=lambda j:(-probs[j],ids[j])),'learned_fused':sorted(fused[:3],key=lambda j:(-probs[j],ids[j])),'combined_tag_graph':combined[:3]}
            for k,pool in [('graph_simple_rerank','lexical'),('graph_feature_rerank','lexical'),('learned_lexical','lexical'),('learned_fused','fused')]:
                if set(ranked[k])!=set(ranked[pool]):raise ValueError('pool drift')
            fam.append({'id':a['id'],'rankings':{k:[ids[j] for j in v] for k,v in ranked.items()},'initial':lp[:1],'second':fused,'max_score':float(probs[lp[0]]),'probs':probs.tolist()})
            for j,b in enumerate(group):
                key=a['id'],b['id']; direct=probs[j]>=.5; atomic_pred=[bool(m.predict([features[key]])[0]) for m in atomic]; ref=i==j
                def claims(row,side,wrong):
                    g=spans(row,side); out=[]
                    for r,(start,end) in g.items():
                        actual=row[side][start:end];out.append((r,start,end,actual))
                    if wrong:
                        role,start,end,actual=out[0];out[0]=('exception',start,end,actual)
                    return out
                drow={'id':list(key),'reference':ref,'direct':bool(direct),'atomic':all(atomic_pred),'facet_truth':facets[key],'facet_pred':atomic_pred,'citations':[]}
                for wrong in (False,True):
                    exact=True; typed=True
                    for row,side in ((a,'query'),(b,'doc')):
                        for role,start,end,actual in claims(row,side,wrong):
                            valid=verify_anchor(row[side],start,end,actual); exact &= valid;typed &= valid and tag_cache[row['id'],side].get(role)==(start,end)
                    drow['citations'].append({'reference_supported':bool(ref and not wrong),'deterministic':bool(direct and exact),'typed':bool(direct and typed)})
                decision_records.append(drow)
            for side in ('doc','query'):
                txt=a[side]; predicted=tag_cache[a['id'],side]
                for role,(start,end) in spans(a,side).items():
                    for claimed,st,en,truth in ((role,start,end,True),(ROLES[(ROLES.index(role)+1)%3],start,end,False),(role,start+1,end,False)):
                        value=txt[start:end]; exact=verify_anchor(txt,st,en,value);typed=exact and predicted.get(claimed)==(st,en)
                        step_records.append({'id':a['id'],'side':side,'role':claimed,'reference':truth,'exact':exact,'typed':typed})
        # Equal additional candidate budget per family (3/6 queries). No reference used to route.
        fixed=set(range(3)); triggered=set(sorted(range(6),key=lambda i:(fam[i]['max_score'],ids[i]))[:3])
        for i,r in enumerate(fam):
            for name,selected in [('fixed_second',fixed),('score_second',triggered)]:
                pool=r['initial']+[j for j in r['second'] if j not in r['initial']][:2] if i in selected else r['initial'];r['rankings'][name]=[ids[j] for j in pool]
            r['rankings']['first_only']=[ids[j] for j in r['initial']]
            r['rankings']['score_abstain']=r['rankings']['first_only'] if r['max_score']>=.5 else []
            r['accepted_top1']=r['rankings']['first_only'][0] if r['rankings']['score_abstain'] else None
        records.extend(fam)
        results[family]={name:{'hit1':sum(r['id'] in r['rankings'][name][:1] for r in fam),'hit3':sum(r['id'] in r['rankings'][name][:3] for r in fam),'candidate_count':sum(len(r['rankings'][name]) for r in fam),'abstain':sum(not r['rankings'][name] for r in fam),'gain_at3':sum(r['id'] in r['rankings'][name][:3] and r['id'] not in r['rankings']['lexical'] for r in fam),'loss_at3':sum(r['id'] not in r['rankings'][name][:3] and r['id'] in r['rankings']['lexical'] for r in fam)} for name in fam[0]['rankings']}
    def binary(data,arm,ref='reference'):
        return {'n':len(data),'tp':sum(r[arm] and r[ref] for r in data),'fp':sum(r[arm] and not r[ref] for r in data),'fn':sum(not r[arm] and r[ref] for r in data),'tn':sum(not r[arm] and not r[ref] for r in data)}
    eval_rows=[r for r in decision_records if r['id'][0].split('-')[0] not in ('PRISMA','CHEERS')]; eval_steps=[r for r in step_records if r['id'].split('-')[0] not in ('PRISMA','CHEERS')];citations=[c for r in eval_rows for c in r['citations']]
    return {'by_family_retrieval':results,'decision_test':{k:binary(eval_rows,k) for k in ('direct','atomic')},'step_test':{k:binary(eval_steps,k) for k in ('exact','typed')},'citation_test':{k:binary(citations,k,'reference_supported') for k in ('deterministic','typed')},'decision_records':decision_records,'step_records':step_records,'retrieval_records':records}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter(); rows=fixture();tag=fit_tagger(rows);result={'protocol':'synthetic-placement-v1','scientific_qualification':False,'semantic_merges':0,'reference':'author-labelled template controls, not independently adjudicated','fresh_model_download_bytes':0,'fixture':rows}
    result['layout']=layout(rows,args.output);result['span_tags']={f:{'rules':span_counts([r for r in rows if r['family']==f],rule_tags),'linear_model':span_counts([r for r in rows if r['family']==f],tag)} for f in FAMILIES};result['pipeline']=pipeline(rows,tag);result['wall_seconds']=time.perf_counter()-start;result['peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (args.output/'synthetic-receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')


if __name__=='__main__':main()
