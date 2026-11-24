"""Frozen diagnostic challenge, not an independent human or admission oracle."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from zipfile import ZipFile

from .classical_linguistic_nlp import compare, load_reference

MODEL = {
    'name': 'en_core_web_sm', 'version': '3.8.0', 'spacy_version': '3.8.11',
    'licence': 'MIT', 'bytes': 12806118,
    'sha256': '1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85',
    'release': 'https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0',
}
FIELDS = {'modality', 'negation', 'quantification', 'logic', 'conditionality', 'roles'}
# Case IDs and expected changed fields are fixed before benchmark execution.
SYNTHETIC = [
    ('synthetic', 's01', 'The nurse must record the result.', 'The nurse should record the result.', ['modality']),
    ('synthetic', 's02', 'Do not report A and report B.', 'Report A and do not report B.', ['negation']),
    ('synthetic', 's03', 'The nurse records the result.', 'The doctor records the result.', ['roles']),
    ('synthetic', 's04', 'The result must be recorded by the nurse.', 'The result must be recorded by the doctor.', ['roles']),
    ('synthetic', 's05', 'Record the result.', 'Record the consent.', ['roles']),
    ('synthetic', 's06', 'If eligible, report A when B is present.', 'If eligible, report A when B is absent.', ['conditionality']),
    ('synthetic', 's07', 'Report A and B or C.', 'Report A or B and C.', ['logic']),
    ('synthetic', 's08', 'Report at least 3 results.', 'Report at most 3 results.', ['quantification']),
    ('synthetic', 's09', 'Report A unless exempt.', 'Report A if exempt.', ['logic', 'conditionality']),
    ('synthetic', 's10', 'Report before discharge.', 'Report after discharge.', ['conditionality']),
    ('synthetic', 's11', 'Do not report A.', 'Do not fail to report A.', ['negation']),
    ('synthetic', 's12', 'Report the result.', 'Report the result.', []),
    ('synthetic', 's13', 'Record the result.', 'Record the result', []),
    ('synthetic', 's14', 'The nurse records the result.', 'The result is recorded by the nurse.', []),
    ('synthetic', 's15', 'Report each result.', 'Report every result.', []),
    ('synthetic', 's16', 'The nurse reports A and records B.', 'The nurse reports B and records A.', ['roles']),
    ('synthetic', 's17', 'Report (A and B) or C.', 'Report A and (B or C).', ['logic']),
]
# Exact, unique short replacements on pinned source rows, not legacy labels.
SOURCE_MUTATIONS = [
    ('prisma-s-2021', '1', 'each individual', 'some individual', ['quantification']),
    ('prisma-s-2021', '2', 'If databases', 'Unless databases', ['logic', 'conditionality']),
    ('prisma-s-2021', '8', 'database and', 'database or', ['logic']),
    ('prisma-s-2021', '9', 'no limits', 'limits', ['negation']),
    ('cheers-2022', '1', 'and specify', 'or specify', ['logic']),
    ('cheers-2022', '6', 'may influence', 'must influence', ['modality']),
    ('cheers-2022', '16', 'If modelling', 'Unless modelling', ['logic', 'conditionality']),
    ('cheers-2022', '22', 'all analytic', 'some analytic', ['quantification']),
]


def mutate(text: str, old: str, new: str) -> str:
    if not old or text.count(old) != 1 or old == new:
        raise ValueError('mutation must identify one exact changed span')
    return text.replace(old, new, 1)


def source_cases(root: Path) -> tuple[list, dict]:
    from .reconcile_authoritative_articles import snapshot_table

    official = root / 'source' / 'official'
    specs = json.loads((official / 'authoritative-article-editions.json').read_text())
    ledger = json.loads((official / 'authoritative-article-rows.json').read_text())
    if ledger.get('schema_version') != 1:
        raise ValueError('unexpected source ledger')
    cases, pins = [], {}
    for edition, item, old, new, expected in SOURCE_MUTATIONS:
        if edition not in pins:
            spec, = [s for s in specs if s['edition'] == edition]
            snapshot, = [s for s in ledger['editions'] if s['edition'] == edition]
            pins[edition] = snapshot_table(snapshot, spec)
        row, = [r for r in pins[edition]['rows'] if r['item_id'] == item]
        group = 'PRISMA' if edition.startswith('prisma') else 'CHEERS'
        case_id = edition + ':' + item
        cases.extend([(group, case_id + ':changed', row['text'], mutate(row['text'], old, new), expected),
                      (group, case_id + ':control', row['text'], row['text'], [])])
    return cases, {e: {k: p[k] for k in ('source_sha256', 'table_rows_sha256', 'doi')} for e, p in pins.items()}


def metrics(rows: list[dict]) -> dict:
    tp = fp = fn = 0
    for row in rows:
        expected, observed = set(row['expected']), set(row['observed'])
        tp += len(expected & observed)
        fp += len(observed - expected)
        fn += len(expected - observed)
    return {'cases': len(rows), 'tp': tp, 'fp': fp, 'fn': fn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'held': sum(r['held'] for r in rows),
            'material_cases': sum(bool(r['expected']) for r in rows),
            'material_no_signal': sum(bool(r['expected']) and not r['observed'] and not r['held'] for r in rows),
            'material_held': sum(bool(r['expected']) and r['held'] for r in rows),
            'controls': sum(not r['expected'] for r in rows),
            'control_false_alert': sum(not r['expected'] and bool(r['observed']) for r in rows)}


def evaluate(cases: list, nlp=None) -> dict:
    rows = []
    for group, case_id, left, right, expected in cases:
        if not set(expected) <= FIELDS or any(r['id'] == case_id for r in rows):
            raise ValueError('invalid benchmark case')
        start = perf_counter()
        result = compare(left, right, nlp)
        elapsed = perf_counter() - start
        fields = set(result.get('changed_fields', []))
        observed = fields & FIELDS
        if 'dependency_negation' in fields:
            observed.add('negation')
        if 'semantic_roles' in fields:
            observed.add('roles')
        # Generic token/sentence hash differences are not semantic predictions.
        rows.append({'group': group, 'id': case_id, 'expected': sorted(expected),
                     'observed': sorted(observed), 'held': result['status'] != 'diagnostic_only',
                     'source_sha256': hashlib.sha256(left.encode()).hexdigest(),
                     'candidate_sha256': hashlib.sha256(right.encode()).hexdigest(),
                     'seconds': elapsed})
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {'method': 'dependency_assisted' if nlp is not None else 'rules',
            'metrics': metrics(rows), 'groups': {g: metrics([r for r in rows if r['group'] == g])
                                                for g in sorted({r['group'] for r in rows})},
            'cases': rows, 'total_comparison_seconds': sum(r['seconds'] for r in rows),
            'process_peak_rss_bytes': rss if sys.platform == 'darwin' else rss * 1024,
            'canonical_packs_promoted': 0}


@contextmanager
def pinned_model(wheel: Path):
    # Verify publisher-pinned bytes before extraction or model loading.
    with wheel.open('rb') as stream:
        raw = stream.read(MODEL['bytes'] + 1)
    if len(raw) != MODEL['bytes'] or hashlib.sha256(raw).hexdigest() != MODEL['sha256']:
        raise ValueError('reference wheel size or digest mismatch')
    from io import BytesIO
    with TemporaryDirectory() as tmp, ZipFile(BytesIO(raw)) as archive:
        archive.extractall(tmp)  # exact verified publisher wheel, never arbitrary archive
        model, reference = load_reference(Path(tmp) / 'en_core_web_sm' / 'en_core_web_sm-3.8.0')
        if reference['spacy_version'] != MODEL['spacy_version'] or reference['model_version'] != MODEL['version']:
            raise ValueError('reference runtime or model version mismatch')
        if model.meta.get('license') != MODEL['licence'] or model.meta.get('name') != 'core_web_sm':
            raise ValueError('reference licence or model identity mismatch')
        yield model


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--synthetic-only', action='store_true')
    parser.add_argument('--model-wheel', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases, pins = ([], {}) if args.synthetic_only else source_cases(args.root)
    cases = SYNTHETIC + cases
    if args.model_wheel:
        with pinned_model(args.model_wheel) as model:
            result = evaluate(cases, model)
    else:
        result = evaluate(cases)
    result.update(schema_version=1, model=MODEL if args.model_wheel else None, source_pins=pins,
                  python=platform.python_version(), platform=platform.platform(),
                  fixture_sha256=hashlib.sha256(json.dumps(cases, ensure_ascii=False).encode()).hexdigest(),
                  label_origin='author-defined challenge labels; independent human review pending',
                  claim_boundary='diagnostic benchmark; no semantic acceptance or pack promotion')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'method': result['method'], **result['metrics']}))


if __name__ == '__main__':
    main()
