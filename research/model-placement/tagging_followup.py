"""Exception-specific fallback and typed-review placement, synthetic development only."""
import argparse
import json
import re
import resource
import time
from pathlib import Path

from synthetic import fixture, fit_tagger, rule_tags, spans, verify_anchor, ROLES

# New author-written stress cases; none entered model training or rules tuning.
# Same family-labelled domains, but NOT independent real guideline families.
STRESS = {
    'CONSORT': [
        ('Trial staff must report adverse events, except events unrelated to treatment.', 'except events unrelated to treatment'),
        ('Report all withdrawals, excluding participants who never enrolled.', 'excluding participants who never enrolled'),
        ('Record allocations other than those made before enrolment.', 'other than those made before enrolment'),
        ('Report protocol deviations unless consent was withdrawn; retain the audit trail.', 'unless consent was withdrawn'),
        ('For interim reviews, report serious events, but not routine screening contacts.', 'but not routine screening contacts'),
        ('Outside the feasibility phase, trial staff must report recruitment rates.', 'Outside the feasibility phase'),
        ('Trial staff must report the reasons for exclusions and the total enrolment.', None),
        ('Trial staff must record all adverse events when follow-up is completed.', None),
    ],
    'STARD': [
        ('Test assessors must record results except when the sample was spoiled.', 'except when the sample was spoiled'),
        ('Report the test threshold, excluding values entered during calibration.', 'excluding values entered during calibration'),
        ('Laboratory staff must retain all specimens other than discarded controls.', 'other than discarded controls'),
        ('Record the comparator unless its use was contraindicated; document the reason.', 'unless its use was contraindicated'),
        ('Describe each reference test, but not tests performed solely for training.', 'but not tests performed solely for training'),
        ('Outside the pilot phase, record the clinical setting.', 'Outside the pilot phase'),
        ('The report must describe exclusions from the analysis.', None),
        ('Test assessors must record the time of collection during repeat sampling.', None),
    ],
    'ARRIVE': [
        ('Research staff must describe housing, except temporary quarantine housing.', 'except temporary quarantine housing'),
        ('Record animal weights, excluding measurements from the acclimatisation period.', 'excluding measurements from the acclimatisation period'),
        ('Describe all cohorts other than the feasibility cohort.', 'other than the feasibility cohort'),
        ('Record food consumption unless food was withheld; note the duration.', 'unless food was withheld'),
        ('Document intervention schedules, but not routine husbandry visits.', 'but not routine husbandry visits'),
        ('Outside the recovery period, record the monitoring interval.', 'Outside the recovery period'),
        ('The analysis must explain the exclusion criteria.', None),
        ('Animal carers must record cage occupancy when animals are transferred.', None),
    ],
    'TRIPOD': [
        ('Model developers must report calibration except for exploratory subgroups.', 'except for exploratory subgroups'),
        ('Report predictor definitions, excluding identifiers removed before modelling.', 'excluding identifiers removed before modelling'),
        ('Describe all validation cohorts other than the development cohort.', 'other than the development cohort'),
        ('Report discrimination unless the outcome was unobserved; provide the denominator.', 'unless the outcome was unobserved'),
        ('Report missing data patterns, but not fields collected only for administration.', 'but not fields collected only for administration'),
        ('Outside the training period, record the source of each validation outcome.', 'Outside the training period'),
        ('Model developers must report the predictor exclusion procedure.', None),
        ('Validation staff must record the outcome definition for external validation.', None),
    ],
}
# Simple extended rule, declared before execution; no fitting. Surface cues only.
CUE = re.compile(r'\b(?:except|unless|excluding|other than|but not|outside)\b[^,.;]+', re.I)


def validate_span(text, span):
    return span is not None and len(span) == 2 and 0 <= span[0] < span[1] <= len(text)


def combine(rule, learned):
    # Only fill a missing exception. Existing actor/condition/rule spans are unchanged.
    out = dict(rule)
    if 'exception' not in out and 'exception' in learned:
        out['exception'] = learned['exception']
    return out


def expanded(text):
    match = CUE.search(text)
    return {'exception': match.span()} if match else {}


def count(gold, predictions):
    if len(gold) != len(predictions):
        raise ValueError('denominator mismatch')
    tp = sum(g is not None and g == p for g, p in zip(gold, predictions, strict=True))
    fp = sum(p is not None and p != g for g, p in zip(gold, predictions, strict=True))
    fn = sum(g is not None and p != g for g, p in zip(gold, predictions, strict=True))
    tn = sum(g is None and p is None for g, p in zip(gold, predictions, strict=True))
    return {'n': len(gold), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
            'coverage': sum(p is not None for p in predictions) / len(gold)}


def evaluate_cases(cases, methods):
    records = []
    for family, ident, text, gold in cases:
        pred = {}
        for arm, method in methods.items():
            span = method(text).get('exception')
            if span is not None and not validate_span(text, span):
                raise ValueError('invalid predicted offset')
            pred[arm] = span
        records.append({'family': family, 'id': ident, 'text': text, 'reference': gold, 'predictions': pred})
    def summarize(rows):
        g = [r['reference'] for r in rows]
        base = [r['predictions']['rules'] for r in rows]
        out = {}
        for arm in methods:
            p = [r['predictions'][arm] for r in rows]
            out[arm] = {**count(g, p), 'gain': sum(a == c and a != b for a,b,c in zip(g,base,p,strict=True)),
                        'loss': sum(a == b and a != c for a,b,c in zip(g,base,p,strict=True))}
        return out
    return {'summary': summarize(records), 'by_family': {f: summarize([r for r in records if r['family']==f]) for f in STRESS}, 'records': records}


def verifier(rows, methods):
    # Review flag, not automatic relationship rejection. Match typed claims on exact anchor.
    records=[]
    for row in rows:
        if row['split'] != 'test':
            continue
        for side in ('doc','query'):
            text=row[side]
            predictions={arm:method(text) for arm,method in methods.items()}
            for role,(start,end) in spans(row,side).items():
                for claimed,a,b,truth in ((role,start,end,True),(ROLES[(ROLES.index(role)+1)%3],start,end,False),(role,start+1,end,False)):
                    exact=verify_anchor(text,a,b,text[start:end]); flags={'exact':not exact}
                    for arm,predicted in predictions.items():
                        flags[arm]=not (exact and predicted.get(claimed)==(a,b))
                    records.append({'family':row['family'],'id':row['id'],'side':side,'role':claimed,'start':a,'end':b,'reference_valid':truth,'review_flags':flags})
    return {'summary': {arm:{'n':len(records),'invalid_flagged':sum(r['review_flags'][arm] and not r['reference_valid'] for r in records),'valid_flagged':sum(r['review_flags'][arm] and r['reference_valid'] for r in records),'invalid_not_flagged':sum(not r['review_flags'][arm] and not r['reference_valid'] for r in records),'valid_not_flagged':sum(not r['review_flags'][arm] and r['reference_valid'] for r in records)} for arm in ('exact',*methods)},'records':records}


def run():
    started=time.perf_counter(); rows=fixture(); learned=fit_tagger(rows)
    methods={'rules':rule_tags,'linear':learned,'fallback':lambda t:combine(rule_tags(t),learned(t)), 'expanded':expanded,'expanded_fallback':lambda t:combine(expanded(t),learned(t))}
    old=[(r['family'],f"{r['id']}-{s}",r[s],spans(r,s)['exception']) for r in rows if r['split']=='test' for s in ('doc','query')]
    new=[]
    for f,cases in STRESS.items():
        for i,(text,gold) in enumerate(cases):
            if gold is not None:
                a=text.index(gold); gold=(a,a+len(gold))
            new.append((f,f'{f}-stress-{i+1}',text,gold))
    result={'protocol':'exception-fallback-stress-v1','scientific_qualification':False,'semantic_merges':0,'model_download_bytes':0,'reference_status':'author-labelled synthetic development only','original':evaluate_cases(old,methods),'stress':evaluate_cases(new,methods),'verifier':verifier(rows,{'typed_rules':rule_tags,'typed_linear':learned,'typed_fallback':methods['fallback']})}
    result['wall_seconds']=time.perf_counter()-started
    result['peak_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.write_text(json.dumps(run(),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
