"""Route every published entry from a matched source census; never admit packs."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
MAX_RECEIPT_BYTES = 30_000_000


def read_receipt(path):
    with path.open('rb') as handle:
        raw = handle.read(MAX_RECEIPT_BYTES + 1)
    if len(raw) > MAX_RECEIPT_BYTES:
        raise ValueError('receipt exceeds size limit')
    return raw


def unique(rows, key):
    out = {row[key]: row for row in rows}
    if len(out) != len(rows):
        raise ValueError('duplicate receipt identity')
    return out


def workplan(catalogue, survey, links):
    revision = catalogue['source_revision']
    if not HEX40.fullmatch(revision) or any(r['source_revision'] != revision for r in (survey, links)):
        raise ValueError('mismatched catalogue revision')
    if survey['summary']['canonical_packs_promoted'] != 0:
        raise ValueError('candidate survey must not promote')
    rows = unique(catalogue['guidelines'], 'id')
    observations = unique(survey['records'], 'id')
    link_rows = unique(links['guidelines'], 'id')
    if (len(rows) != catalogue['published_count'] or set(rows) != set(observations)
            or set(rows) != set(link_rows) or survey['summary']['published_count'] != len(rows)
            or links['published_count'] != len(rows)):
        raise ValueError('incomplete directory coverage')
    by_pmcid = {}
    for row in survey.get('priority_articles', []) + survey.get('bulk_articles', []):
        by_pmcid.setdefault(row['pmcid'], []).append(row)
    work = []
    for key, entry in sorted(rows.items()):
        observation, link = observations[key], link_rows[key]
        blob = entry['source_blob_sha']
        if not HEX40.fullmatch(blob) or any(x['source_blob_sha'] != blob for x in (observation, link)):
            raise ValueError('source blob mismatch')
        status, pmcid = observation['status'], observation.get('pmcid')
        evidence = by_pmcid.get(pmcid, [])
        action = 'resolve_identity'
        if observation.get('provider_disagreements') or status in {'identifier_conflict', 'ambiguous_identifier'}:
            action = 'hold_identity_conflict'
        elif status == 'lookup_incomplete':
            action = 'resume_provider_lookup'
        elif status == 'oa_xml_candidate':
            action = 'acquire_exact_source'
            if len(evidence) > 1 or any(e.get('doi') != observation.get('resolved_doi') for e in evidence):
                action = 'hold_source_binding'
            elif evidence:
                source = evidence[0]
                source_hash = source.get('source_sha256')
                if source_hash is not None and not HEX64.fullmatch(source_hash):
                    raise ValueError('invalid source fingerprint')
                if source.get('source_blobs') is not None and [key, blob] not in source['source_blobs']:
                    action = 'hold_source_binding'
                elif source['status'] == 'deferred_acquisition_budget':
                    action = 'resume_acquisition_budget'
                elif source['status'] == 'held':
                    action = 'retry_acquisition_or_alternative'
                elif source.get('source_sha256') and source.get('matched_rows'):
                    action = 'qualify_structure_rights_and_interpretation'
                elif source.get('source_sha256'):
                    action = 'extract_anchored_candidates'
        elif link.get('candidates'):
            action = 'qualify_source_link'
        elif status == 'metadata_only':
            action = 'locate_authoritative_source'
        work.append({'id': key, 'source_blob_sha': blob, 'lookup_status': status,
                     'pmcid': pmcid, 'link_candidates': len(link.get('candidates', [])),
                     'next_action': action, 'admission': 'not_assessed'})
    return {'schema_version': 1, 'source_revision': revision, 'published_count': len(work),
            'lookup_counts': dict(sorted(Counter(x['lookup_status'] for x in work).items())),
            'next_action_counts': dict(sorted(Counter(x['next_action'] for x in work).items())),
            'canonical_packs_promoted': 0, 'records': work}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--survey', type=Path, required=True)
    parser.add_argument('--links', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = {key: read_receipt(getattr(args, key)) for key in ('catalogue', 'survey', 'links')}
    report = workplan(*(json.loads(raw[key]) for key in ('catalogue', 'survey', 'links')))
    report['input_sha256s'] = {k: hashlib.sha256(v).hexdigest() for k, v in raw.items()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'records'}, sort_keys=True))


if __name__ == '__main__':
    main()
