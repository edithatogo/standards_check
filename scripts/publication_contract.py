"""Validate immutable profile versions and a rights-safe publication evidence snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

from .directory_workplan import workplan, read_receipt, MAX_RECEIPT_BYTES

PROFILE = Path('specifications/reporting-guideline-interoperability')
VERSION = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)')
HEX64 = re.compile(r'[0-9a-f]{64}')


def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw, usedforsecurity=False).hexdigest()


def validate_versions(root, registry, prior=None):
    versions = registry['versions']
    keys = [v['version'] for v in versions]
    if (registry['schema_version'] != 1 or not keys or len(keys) != len(set(keys))
            or any(not VERSION.fullmatch(v) for v in keys)
            or keys != sorted(keys, key=lambda v: tuple(map(int, v.split('.'))))
            or registry['current_draft'] != keys[-1]):
        raise ValueError('invalid version sequence')
    approved = []
    receipt = {}
    for entry in versions:
        version = entry['version']
        path = root / PROFILE / (version + '.md')
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing immutable profile snapshot')
        raw = path.read_bytes()
        if blob_sha(raw) != entry['git_blob_sha']:
            raise ValueError('profile snapshot changed')
        approval = entry['approval']
        if entry['status'] == 'approved':
            if not isinstance(approval, dict) or not all(approval.get(k) for k in ('owner', 'date', 'decision_url')):
                raise ValueError('approved profile requires explicit owner decision')
            approved.append(version)
        elif entry['status'] != 'draft' or approval is not None:
            raise ValueError('invalid draft or approval state')
        receipt[version] = {'sha256': hashlib.sha256(raw).hexdigest(), 'status': entry['status']}
    if registry['approved_version'] != (approved[-1] if approved else None):
        raise ValueError('approved pointer disagrees with decisions')
    if prior is not None:
        current = {v['version']: v for v in versions}
        for previous in prior['versions']:
            newer = current.get(previous['version'])
            if newer is None or newer['git_blob_sha'] != previous['git_blob_sha']:
                raise ValueError('published version history must be immutable')
            if previous['status'] == 'approved' and newer != previous:
                raise ValueError('approved decision history must be immutable')
    return receipt


def validate_evidence(evidence):
    if evidence['schema_version'] != 1 or evidence['status'] != 'historical_descriptive':
        raise ValueError('unexpected publication evidence scope')
    directory = evidence['directory']
    for counts in ('lookup_counts', 'next_action_counts'):
        values = directory[counts].values()
        if any(type(v) is not int or v < 0 for v in values) or sum(values) != directory['published_count']:
            raise ValueError('directory denominator does not conserve')
    if directory['canonical_packs_promoted'] != 0:
        raise ValueError('directory candidate evidence cannot admit packs')
    for record in evidence['receipts']:
        if not HEX64.fullmatch(record['sha256']) or not record['url'].startswith('https://github.com/'):
            raise ValueError('invalid evidence reference')
    nli = evidence['five_class_controls']
    n = nli['n']
    if not (0 <= nli['correct_consensus'] <= nli['consensus'] <= n
            and 0 <= nli['minilm_correct'] <= n and 0 <= nli['deberta_correct'] <= n
            and nli['deberta_correct'] - nli['minilm_correct'] == nli['fixed'] - nli['introduced']):
        raise ValueError('semantic cohort counts do not conserve')
    if nli['qualified'] is not False or nli['natural_consensus'] != 0:
        raise ValueError('historical witness failure must not be relabelled')
    return {'directory_entries': directory['published_count'], 'formal_control_pairs': n,
            'scientific_qualification': 'held', 'submission_authorized': False}


def replay_directory(evidence, artifact):
    pin, = [r for r in evidence['receipts'] if r['kind'] == 'directory']
    raw = read_receipt(artifact)
    if hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('directory artifact digest mismatch')
    from io import BytesIO
    names = {'catalogue': 'equator-catalogue.json', 'survey': 'equator-article-survey.json',
             'links': 'equator-source-link-candidates.json'}
    with ZipFile(BytesIO(raw)) as archive:
        parts = {}
        for key, name in names.items():
            members = [m for m in archive.infolist() if m.filename == name]
            if len(members) != 1 or members[0].file_size > MAX_RECEIPT_BYTES:
                raise ValueError('ambiguous or oversized receipt member')
            parts[key] = archive.read(members[0])
    result = workplan(*(json.loads(parts[key]) for key in ('catalogue', 'survey', 'links')))
    result['input_sha256s'] = {k: hashlib.sha256(v).hexdigest() for k, v in parts.items()}
    if {k: v for k, v in result.items() if k != 'records'} != evidence['directory']:
        raise ValueError('directory publication claim differs from replay')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline-ref')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--directory-artifact', type=Path, help='Optional exact historical artifact ZIP')
    args = parser.parse_args()
    registry = json.loads((args.root / PROFILE / 'versions.json').read_text())
    prior = None
    if args.baseline_ref:
        if not re.fullmatch(r'[0-9a-f]{40}', args.baseline_ref):
            raise ValueError('baseline must be an exact Git commit')
        relative = (PROFILE / 'versions.json').as_posix()
        # A first introduction has no baseline registry; subsequent versions must conserve it.
        listing = subprocess.check_output(['git', 'ls-tree', args.baseline_ref, '--', relative], cwd=args.root)
        if listing:
            prior = json.loads(subprocess.check_output(['git', 'show', args.baseline_ref + ':' + relative], cwd=args.root))
    evidence = json.loads((args.root / 'publication/evidence-2026-11-24.json').read_text())
    result = {'profile_versions': validate_versions(args.root, registry, prior),
              'publication': validate_evidence(evidence), 'directory_replayed': False}
    if args.directory_artifact:
        replay_directory(evidence, args.directory_artifact)
        result['directory_replayed'] = True
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
