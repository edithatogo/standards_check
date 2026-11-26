"""Noncompensatory exploratory tool selection and catalogue crosswalk coverage."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

from .vector_classification import ARCHIVE_SHA, FACETS


MAXIMIZE = ('recall', 'precision', 'macro_label_recall')
CRITERIA = (*MAXIMIZE, 'seconds')


def measured(row):
    return all(type(row.get(k)) in (int, float) and math.isfinite(row[k]) and row[k] >= 0
               and (k == 'seconds' or row[k] <= 1) for k in CRITERIA)


def dominates(a, b):
    if not measured(a) or not measured(b):
        return False
    return (all(a[k] >= b[k] for k in MAXIMIZE) and a['seconds'] <= b['seconds']
            and (any(a[k] > b[k] for k in MAXIMIZE) or a['seconds'] < b['seconds']))


def frontier(arms):
    known = {k: v for k, v in arms.items() if measured(v)}
    return {'pareto': sorted(k for k, v in known.items()
                             if not any(dominates(other, v) for j, other in known.items() if j != k)),
            'unmeasured': sorted(set(arms) - set(known))}


def crosswalk_coverage(catalogue, mappings):
    result = {}
    for facet in FACETS:
        observed = {label for row in catalogue['guidelines'] for label in (row.get(facet) or [])}
        pairs = mappings.get(facet, {})
        if set(pairs) - observed or any(not ids or len(ids) != len(set(ids)) or
                any(not re.fullmatch(r'D\d{6,9}', value) for value in ids) for ids in pairs.values()):
            raise ValueError('invalid or unobserved crosswalk')
        result[facet] = {'observed_labels': len(observed), 'mapped_labels': len(pairs),
                         'unmapped_labels': sorted(observed - set(pairs)), 'admission': 'candidate_only'}
    return result


def compare(report):
    results = {}
    for facet in FACETS:
        arms = {}
        for name, value in report['arms'].items():
            m = value['facets'][facet]['metrics']
            per_label = m['per_label']
            arms[name] = {'recall': m['macro_recall_at_3'], 'precision': m['precision_at_3'],
                          'macro_label_recall': (sum(x['hits_at_3']/x['positives'] for x in per_label.values())/len(per_label)
                                          if per_label else None),
                          'seconds': value['seconds']}
        results[facet] = {'criteria': arms, **frontier(arms), 'production_eligible': [],
                          'hold': 'No independent reference, qualified family lock or repeated cost measurement.'}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--report-sha256', required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--crosswalk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.report.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.report_sha256:
        raise ValueError('factorial report digest mismatch')
    archive = args.archive.read_bytes()
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA:
        raise ValueError('catalogue digest mismatch')
    with zipfile.ZipFile(args.archive) as z:
        catalogue = json.loads(z.read('equator-catalogue.json'))
    mappings = json.loads(args.crosswalk.read_bytes())
    result = {'report_sha256': args.report_sha256, 'catalogue_sha256': ARCHIVE_SHA,
              'crosswalk_sha256': hashlib.sha256(args.crosswalk.read_bytes()).hexdigest(),
              'crosswalk': crosswalk_coverage(catalogue, mappings['mappings']),
              'development_selection': compare(json.loads(raw)),
              'boundary': 'Descriptive Pareto only. macro_label_recall weights each observed label equally; no universal weights or production admission.'}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
