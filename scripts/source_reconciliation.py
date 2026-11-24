"""Offline, text-free reconciliation diagnostics; never promote a canonical pack."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from difflib import SequenceMatcher
from itertools import combinations
import hashlib
import json
from pathlib import Path
import re
import unicodedata


VERSION = '1'
PATTERNS = {
    'polarity': r"\b(?:not|no|never|without|neither|nor|cannot|\w+n['’]t)\b",
    'modality': r'\b(?:must|should|may|might|shall|can|required|recommended|optional)\b',
    'logic': r'\b(?:and|or|both|either|neither|nor)\b',
    'quantity': r'\b(?:at least|at most|more than|less than|all|each|every|any|some|none|only|one|two|three)\b|\d+(?:[.,]\d+)*%?',
    'condition': r'\b(?:if|unless|when|where|except|provided that|as applicable|where applicable|if applicable)\b',
    'temporal': r'\b(?:before|after|during|until|since|prior to|following|within)\b',
}
TOKEN = re.compile(r"\d+(?:[.,]\d+)*%?|\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)
FIELD = re.compile(r'\S+(?: \S+)*')
ITEM = re.compile(r'\d{1,3}\.\d{1,3}')


def normalized(text: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', text).split())


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fingerprint(text: str) -> str:
    return sha(normalized(text).encode())


def linguistic_compare(source: str, candidate: str) -> dict:
    """Classical rule-based markers with local context; not an entailment oracle."""
    a, b = normalized(source), normalized(candidate)
    left, right = TOKEN.findall(a.casefold()), TOKEN.findall(b.casefold())
    findings = []
    for name, pattern in PATTERNS.items():
        def markers(text: str) -> list:
            result = []
            for clause in re.split(r'[;!?]|\.(?=\s|$)', text.casefold()):
                for match in re.finditer(pattern, clause):
                    result.append((match.group(), tuple(TOKEN.findall(clause[:match.start()])[-2:]),
                                   tuple(TOKEN.findall(clause[match.end():])[:2])))
            return result
        if markers(a) != markers(b):
            findings.append(name)
    if left != right:
        findings.append('lexical')
    if re.findall(r'[^\w\s]', a) != re.findall(r'[^\w\s]', b):
        findings.append('punctuation')
    if a != b and not findings:
        findings.append('surface')
    return {'exact': a == b, 'source_sha256': fingerprint(a), 'candidate_sha256': fingerprint(b),
            'similarity_permille': round(1000 * SequenceMatcher(None, left, right, autojunk=False).ratio()),
            'findings': sorted(findings)}


def layout_rows(layout: str) -> tuple[list[dict], list[str]]:
    """Reconstruct full candidate rows from independent Poppler layout text.

    Only explicit one-line headers and unambiguous column/continuation geometry
    are supported. No identifier-only match or ambiguous row gets a text digest.
    """
    rows, issues = [], set()
    for page, text in enumerate(layout.split('\f'), 1):
        if not text.strip():
            continue
        starts, roles, current = [], {}, None

        def finish():
            nonlocal current
            if current is not None:
                item, start, end, parts, bad = current
                rows.append({'item_id': item, 'identifier_anchor': f'page/{page}/line/{start}',
                             'requirement_anchor': f'page/{page}/lines/{start}-{end}',
                             'requirement_sha256': fingerprint(' '.join(parts)) if parts and not bad else None})
                current = None

        for number, line in enumerate(text.splitlines(), 1):
            fields = list(FIELD.finditer(line))
            if not fields:
                continue
            labels = [re.sub(r'[^a-z0-9]', '', f.group().casefold()) for f in fields]
            if 'subitemnumber' in labels and 'subitem' in labels:
                finish()
                if labels.count('subitemnumber') != 1 or labels.count('subitem') != 1:
                    issues.add('ambiguous_header'); starts = []; continue
                starts = [f.start() for f in fields]
                roles = {k: labels.index(v) for k, v in [('id', 'subitemnumber'), ('req', 'subitem')]}
                continue
            if not starts:
                issues.add('missing_header'); continue
            cells, invalid = {}, False
            for field in fields:
                column = bisect_right(starts, field.start()) - 1
                if column < 0 or (column + 1 < len(starts) and field.end() > starts[column + 1]):
                    invalid = True; continue
                cells.setdefault(column, []).append(field.group())
            identifier = ' '.join(cells.get(roles['id'], []))
            requirement = ' '.join(cells.get(roles['req'], []))
            if ITEM.fullmatch(identifier):
                finish()
                current = [identifier, number, number, [requirement] if requirement else [], invalid or not requirement]
                if current[-1]:
                    issues.add('incomplete_row')
            elif not identifier and requirement and set(cells) == {roles['req']} and current and not invalid:
                current[2] = number; current[3].append(requirement)
            else:
                issues.add('unbound_layout_line')
                if current:
                    current[-1] = True
        finish()
    counts = Counter(r['item_id'] for r in rows)
    for row in rows:
        if counts[row['item_id']] > 1:
            issues.add('duplicate_id'); row['requirement_sha256'] = None
    return rows, sorted(issues)


def item_findings(source: dict, legacy: list[dict]) -> dict:
    numbered = [r for r in legacy if r['declared_item_id'] == source['item_id']]
    exact = [r for r in legacy if normalized(r['text']) == normalized(source['text'])]
    if len(numbered) > 1 or len(exact) > 1 or (numbered and exact and numbered[0] != exact[0]):
        return {'status': 'held_ambiguous_alignment', 'legacy_position': None, 'findings': [], 'similarity_permille': None}
    candidates = numbered or exact
    if not candidates:
        return {'status': 'held_unaligned', 'legacy_position': None, 'findings': [], 'similarity_permille': None}
    match = candidates[0]
    if match['declared_item_id'] not in (None, '', source['item_id']):
        return {'status': 'held_ambiguous_alignment', 'legacy_position': None, 'findings': [], 'similarity_permille': None}
    comparison = linguistic_compare(source['text'], match['text'])
    return {'status': 'exact_text_candidate' if comparison['exact'] else 'held_text_discrepancy',
            'legacy_position': match['position'], 'findings': comparison['findings'],
            'similarity_permille': comparison['similarity_permille']}


# Explicit, nullable columns; no candidate prose, model output or raw parser data.
SCHEMAS = {
    'guidelines': {'key': 'str', 'kind': 'str', 'version': 'str', 'rights': 'str', 'status': 'str'},
    'sources': {'key': 'str', 'guideline_id': 'str', 'source_sha256': 'str', 'source_blob_sha': 'str', 'format': 'str', 'status': 'str'},
    'requirements': {'key': 'str', 'source_id': 'str', 'item_id': 'str', 'ordinal': 'int', 'fingerprint': 'str', 'rights': 'str'},
    'canonical_requirements': {'key': 'str', 'requirement_id': 'str', 'display_number': 'str', 'section': 'str',
                               'verbatim_text': 'str', 'normalized_requirement': 'str', 'guidance': 'str', 'rights': 'str',
                               'spdx': 'str', 'license_url': 'str', 'attribution': 'str', 'redistribution': 'str',
                               'source_url': 'str', 'evidence_expectations_json': 'str'},
    'format_comparisons': {'key': 'str', 'left_source_id': 'str', 'right_source_id': 'str', 'item_id': 'str',
                           'left_requirement_id': 'str', 'right_requirement_id': 'str', 'status': 'str'},
    'source_anchors': {'key': 'str', 'requirement_id': 'str', 'anchor': 'str'},
    'comparisons': {'key': 'str', 'requirement_id': 'str', 'status': 'str', 'legacy_position': 'int', 'findings': 'str', 'similarity_permille': 'int'},
    'admission_decisions': {'key': 'str', 'source_id': 'str', 'requirement_id': 'str', 'disposition': 'str', 'independent_sample': 'bool'},
    'extraction_runs': {'key': 'str', 'source_id': 'str', 'parser': 'str', 'version': 'str', 'rows': 'int',
                        'issues_json': 'str', 'identity': 'str', 'exact_expected_order': 'bool'},
}


def project(catalogue: dict, packs: list[dict], article: dict, ecoevo: dict, legacy: dict) -> dict:
    tables = {name: [] for name in SCHEMAS}

    def add(table, **row):
        tables[table].append(row)

    def source(key, gid, digest, fmt, status, blob=None):
        add('sources', key=key, guideline_id=gid, source_sha256=digest, source_blob_sha=blob, format=fmt, status=status)

    def requirement(sid, ordinal, item, digest, anchor, rights):
        key = f'{sid}/{ordinal}'
        add('requirements', key=key, source_id=sid, item_id=item, ordinal=ordinal, fingerprint=digest, rights=rights)
        add('source_anchors', key=key, requirement_id=key, anchor=anchor)
        return key

    def decision(sid, key, disposition, sample=False):
        add('admission_decisions', key=key or sid, source_id=sid, requirement_id=key,
            disposition=disposition, independent_sample=sample)

    for row in catalogue['guidelines']:
        gid = row['id']
        add('guidelines', key=gid, kind='discovery', version=None, rights='unassessed', status='discovery_only')
        source(gid + '/directory', gid, None, 'QMD', 'discovery_only', row['source_blob_sha'])
    for pack in packs:
        gid = 'pack:' + pack['pack_id']
        rights, status = pack['rights']['status'], pack['verification']['status']
        add('guidelines', key=gid, kind='canonical_pack', version=pack['version'], rights=rights, status=status)
        sid = gid + '/authority'
        source(sid, gid, pack['authority'].get('source_sha256'), 'canonical_pack', status)
        for i, row in enumerate(pack['requirements'], 1):
            policy = pack['rights'] if row['rights'].get('inherit_from_pack') else row['rights']
            effective = policy.get('status', 'unassessed')
            key = requirement(sid, i, row['id'], fingerprint(row['verbatim_text']) if row.get('verbatim_text') else None,
                              row['source_anchor'], effective)
            # Only already-admitted pack content with effective cleared rights may carry prose.
            add('canonical_requirements', key=key, requirement_id=key, display_number=row.get('display_number'),
                section=row.get('section') if effective == 'cleared' else None,
                verbatim_text=row.get('verbatim_text') if effective == 'cleared' else None,
                normalized_requirement=row.get('normalized_requirement') if effective == 'cleared' else None,
                guidance=row.get('guidance') if effective == 'cleared' else None, rights=effective,
                spdx=policy.get('spdx'), license_url=policy.get('license_url'),
                attribution=policy.get('attribution'), redistribution=policy.get('redistribution'),
                source_url=pack['authority'].get('source_url'),
                evidence_expectations_json=json.dumps(row.get('evidence_expectations', [])))
    for edition in article['editions']:
        name = edition['edition']; gid = 'article:' + name; sid = gid + '/table'
        add('guidelines', key=gid, kind='candidate', version=None, rights='unassessed', status=edition['status'])
        src = edition.get('source', {})
        source(sid, gid, src.get('source_sha256'), 'JATS', edition['status'])
        rows = src.get('rows', [])
        add('extraction_runs', key=sid, source_id=sid, parser='retained_or_jats', version=VERSION, rows=len(rows),
            issues_json=json.dumps(src.get('structure', {}).get('issues', [])), identity=src.get('pin_status'),
            exact_expected_order=None)
        if not rows:
            decision(sid, None, 'held_source')
        exact = []
        for i, row in enumerate(rows, 1):
            key = requirement(sid, i, row['item_id'], fingerprint(row['text']), row['source_anchor'], 'unassessed')
            result = item_findings(row, legacy.get(name, []))
            add('comparisons', key=key, requirement_id=key, status=result['status'], legacy_position=result['legacy_position'],
                findings=','.join(result['findings']), similarity_permille=result['similarity_permille'])
            decision(sid, key, 'held_independent_review' if result['status'] == 'exact_text_candidate' else result['status'])
            if result['status'] == 'exact_text_candidate':
                exact.append(tables['admission_decisions'][-1])
        # Deterministic review sample (at least one per edition if any exact candidates).
        for selected in sorted(exact, key=lambda r: sha(r['key'].encode()))[:max(1, (len(exact)+9)//10)]:
            selected['independent_sample'] = True
    if ecoevo['sources']:
        gid = 'candidate:prisma-ecoevo-2021'
        add('guidelines', key=gid, kind='candidate', version='2021', rights='unassessed', status='held')
        format_groups = {}
        for observed in ecoevo['sources']:
            for parser, rows in [('native', observed['rows']), ('poppler', observed.get('poppler_rows'))]:
                if rows is None:
                    continue
                sid = gid + '/' + observed['path'] + '/' + parser
                source(sid, gid, observed.get('source_sha256'), Path(observed['path']).suffix, 'held')
                add('extraction_runs', key=sid, source_id=sid, parser=parser,
                    version=observed.get('poppler_version' if parser == 'poppler' else 'pdfplumber_version'), rows=len(rows),
                    issues_json=json.dumps(observed.get('poppler_row_issues' if parser == 'poppler' else 'issues', [])),
                    identity=observed.get('identity'),
                    exact_expected_order=observed.get('poppler_exact_expected_order' if parser == 'poppler' else 'exact_expected_order'))
                if not rows:
                    decision(sid, None, 'held_source')
                format_groups[sid] = {}
                for i, row in enumerate(rows, 1):
                    key = requirement(sid, i, row['item_id'], row['requirement_sha256'], row['requirement_anchor'], 'unassessed')
                    decision(sid, key, 'held_independent_review' if row['requirement_sha256'] else 'held_incomplete_row')
                    format_groups[sid].setdefault(row['item_id'], []).append((key, row['requirement_sha256']))
        for left, right in combinations(sorted(format_groups), 2):
            a, b = format_groups[left], format_groups[right]
            for item in sorted(set(ecoevo.get('expected_item_ids', [])) | a.keys() | b.keys()):
                l, r = a.get(item, []), b.get(item, [])
                lk, lh = l[0] if len(l) == 1 else (None, None)
                rk, rh = r[0] if len(r) == 1 else (None, None)
                status = ('held_missing_or_ambiguous' if not lh or not rh else
                          'exact_fingerprint_candidate' if lh == rh else 'held_text_discrepancy')
                add('format_comparisons', key=sha(json.dumps([left, right, item]).encode()), left_source_id=left,
                    right_source_id=right, item_id=item, left_requirement_id=lk, right_requirement_id=rk, status=status)
    validate_tables(tables)
    return tables


def validate_tables(tables: dict) -> None:
    if set(tables) != set(SCHEMAS):
        raise ValueError('unexpected analytical tables')
    keys = {}
    for table, rows in tables.items():
        if any(set(row) != set(SCHEMAS[table]) for row in rows):
            raise ValueError('unexpected analytical columns')
        expected_types = {'str': str, 'int': int, 'bool': bool}
        if any(value is not None and type(value) is not expected_types[SCHEMAS[table][col]]
               for row in rows for col, value in row.items()):
            raise ValueError('unexpected analytical value type')
        keys[table] = {row['key'] for row in rows}
        if None in keys[table] or '' in keys[table]:
            raise ValueError('missing analytical key')
        if len(keys[table]) != len(rows):
            raise ValueError('duplicate analytical key')
    for table, field, parent in [('sources', 'guideline_id', 'guidelines'), ('requirements', 'source_id', 'sources'),
                                 ('source_anchors', 'requirement_id', 'requirements'), ('comparisons', 'requirement_id', 'requirements'),
                                 ('canonical_requirements', 'requirement_id', 'requirements'),
                                 ('format_comparisons', 'left_source_id', 'sources'), ('format_comparisons', 'right_source_id', 'sources'),
                                 ('format_comparisons', 'left_requirement_id', 'requirements'), ('format_comparisons', 'right_requirement_id', 'requirements'),
                                 ('admission_decisions', 'source_id', 'sources'), ('admission_decisions', 'requirement_id', 'requirements'),
                                 ('extraction_runs', 'source_id', 'sources')]:
        if any(row[field] not in keys[parent] and not (table in {'admission_decisions', 'format_comparisons'} and field.endswith('requirement_id') and row[field] is None)
               for row in tables[table]):
            raise ValueError('unbound analytical relationship')


def write_parquet(tables: dict, output: Path) -> dict:
    import polars as pl
    validate_tables(tables)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    types = {'str': pl.String, 'int': pl.Int64, 'bool': pl.Boolean}
    for name, rows in tables.items():
        schema = {col: types[kind] for col, kind in SCHEMAS[name].items()}
        frame = pl.DataFrame(rows, schema=schema, strict=True).sort('key')
        path = output / (name + '.parquet')
        frame.write_parquet(path, compression='zstd')
        if not pl.read_parquet(path).equals(frame):
            raise ValueError('Parquet conservation failure')
        manifest[name] = {'rows': frame.height, 'sha256': sha(path.read_bytes()), 'schema': SCHEMAS[name]}
    return {'polars_version': pl.__version__, 'tables': manifest}


def main() -> None:
    from .reconcile_authoritative_articles import audit, parse_legacy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--ecoevo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--survey', type=Path, help='Optional already-acquired catalogue survey receipt, never fetches sources')
    args = parser.parse_args()
    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))
    specs = read(args.root / 'source/official/authoritative-article-editions.json')
    article = audit(args.root, None, specs)
    legacy = {spec['edition']: parse_legacy((args.root / spec['legacy_path']).read_text(encoding='utf-8')) for spec in specs
              if (args.root / spec['legacy_path']).is_file()}
    catalogue = read(args.root / 'source/equator/discovery.json')
    packs = [read(path) for path in sorted((args.root / 'packs').rglob('pack.json'))]
    ecoevo = read(args.ecoevo)
    tables = project(catalogue, packs, article, ecoevo, legacy)
    if args.survey:
        from .review_source_receipts import review
        survey = read(args.survey)
        retrospective = review(survey)
        # Existing receipt reviewer owns the queue and status taxonomy; keep this separate
        # from pack authority and the pinned discovery catalogue.
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'survey-retrospective.json').write_text(json.dumps(retrospective, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = write_parquet(tables, args.output)
    receipt = {'schema_version': VERSION, 'revision': args.revision, 'canonical_packs_promoted': 0,
               'ecoevo_sha256': sha(args.ecoevo.read_bytes()), 'catalogue_revision': catalogue.get('source_revision'),
               'survey_sha256': sha(args.survey.read_bytes()) if args.survey else None,
               'article_receipt_sha256': sha(json.dumps(article, sort_keys=True).encode()),
               'pack_sha256s': {pack['pack_id']: sha(json.dumps(pack, sort_keys=True).encode()) for pack in packs},
               'dispositions': dict(sorted(Counter(r['disposition'] for r in tables['admission_decisions']).items())),
               **manifest}
    (args.output / 'manifest.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(receipt['dispositions'], sort_keys=True))


if __name__ == '__main__':
    main()
