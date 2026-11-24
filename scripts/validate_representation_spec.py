"""Check immutable representation-profile versions; never grant scientific approval."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


REGISTRY = 'contracts/representation/releases.json'
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')
DIGEST = re.compile(r'[0-9a-f]{64}')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_pin(relative: str, digest: str) -> None:
    require(isinstance(relative, str) and relative, 'missing profile path')
    path = PurePosixPath(relative)
    require(not path.is_absolute() and '..' not in path.parts and '\\' not in relative,
            'profile path escapes repository')
    require(isinstance(digest, str) and DIGEST.fullmatch(digest), 'invalid profile digest')


def bound_file(root: Path, relative: str, digest: str) -> bytes:
    check_pin(relative, digest)
    target = (root / relative).resolve()
    require(target.is_relative_to(root.resolve()) and target.is_file(), 'missing or escaping profile file')
    raw = target.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, f'profile digest mismatch: {relative}')
    return raw


def prior_registry(root: Path, revision: str) -> dict | None:
    require(bool(re.fullmatch(r'[0-9a-f]{40}', revision)), 'baseline must be an exact commit')
    def git(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=False)
        require(result.returncode == 0, 'unavailable profile baseline')
        return result.stdout
    git('cat-file', '-e', revision + '^{commit}')
    if not git('ls-tree', revision, '--', REGISTRY).strip():
        return None  # The first registry is an explicit initial version.
    return json.loads(git('show', revision + ':' + REGISTRY))


def validate(root: Path, baseline_revision: str | None = None) -> dict:
    registry = json.loads((root / REGISTRY).read_text(encoding='utf-8'))
    require(set(registry) == {'schema_version', 'profile_id', 'current_version',
                              'approved_version', 'releases'}, 'unexpected profile registry fields')
    require(registry['schema_version'] == 'dev.standardflow.representation-registry.v1',
            'unsupported profile registry version')
    require(registry['profile_id'] == 'dev.standardflow.reporting-guideline-representation',
            'unexpected profile identity')
    releases = registry['releases']
    require(isinstance(releases, list) and releases, 'missing profile releases')
    versions, approved, previous = [], [], None
    for release in releases:
        require(set(release) == {'version', 'status', 'document', 'sha256', 'previous_version',
                                 'compatibility', 'requirement_ids', 'implementation_contracts',
                                 'approval'}, 'unexpected profile release fields')
        version = release['version']
        require(isinstance(version, str) and VERSION.fullmatch(version), 'invalid profile version')
        require(version not in versions, 'duplicate profile version')
        require(release['previous_version'] == previous, 'broken profile version chain')
        if previous:
            require(tuple(map(int, version.split('.'))) > tuple(map(int, previous.split('.'))),
                    'profile versions must increase')
        require(release['compatibility'] in ({'initial'} if previous is None else
                                             {'clarification', 'additive', 'breaking'}),
                'missing compatibility classification')
        if previous and release['compatibility'] == 'breaking':
            old, new = tuple(map(int, previous.split('.'))), tuple(map(int, version.split('.')))
            require(new[0] > old[0] or (old[0] == new[0] == 0 and new[1] > old[1]),
                    'breaking changes require a major version, or minor before 1.0')
        if previous and release['compatibility'] == 'additive':
            require(tuple(map(int, version.split('.')[:2])) > tuple(map(int, previous.split('.')[:2])),
                    'additive changes require at least a minor version')
        raw = bound_file(root, release['document'], release['sha256'])
        assertions = re.findall(r'^\| (RGI-[0-9]{2,}) \| (?:Must|Should|Could|Won\'t) \|',
                                raw.decode('utf-8'), re.MULTILINE)
        require(assertions and assertions == release['requirement_ids'] and
                len(set(assertions)) == len(assertions), 'profile requirement IDs differ from specification')
        contracts = release['implementation_contracts']
        require(isinstance(contracts, list) and contracts, 'missing implementation contract pins')
        require(all(set(item) == {'path', 'sha256'} for item in contracts), 'invalid contract pin')
        require(len({item['path'] for item in contracts}) == len(contracts), 'duplicate contract pin')
        for item in contracts:
            check_pin(item['path'], item['sha256'])
        # Historical releases retain their original pins. Only the current implementation
        # must match the current profile; old bytes remain retrievable in Git history.
        if version == registry['current_version']:
            for item in contracts:
                bound_file(root, item['path'], item['sha256'])
        require(release['status'] in {'draft', 'approved'}, 'invalid profile approval state')
        approval = release['approval']
        if release['status'] == 'draft':
            require(approval is None, 'draft cannot contain an approval')
        else:
            require(isinstance(approval, dict) and set(approval) ==
                    {'actor', 'decision', 'decision_url', 'date', 'specification_sha256'},
                    'approved profile requires an explicit approval receipt')
            require(isinstance(approval['actor'], str) and approval['actor'].strip() and
                    approval['decision'] == 'approve' and
                    approval['specification_sha256'] == release['sha256'],
                    'approval must identify actor, decision and exact specification digest')
            require(isinstance(approval['decision_url'], str) and
                    re.fullmatch(r'https://github\.com/[^/\s]+/[^/\s]+/(?:issues|pull)/[1-9][0-9]*(?:#[^\s]+)?',
                                 approval['decision_url']), 'approval requires a durable decision URL')
            require(isinstance(approval['date'], str), 'approval date must be ISO formatted')
            date.fromisoformat(approval['date'])
            approved.append(version)
        versions.append(version)
        previous = version
    require(registry['current_version'] == versions[-1], 'current profile must be the latest version')
    require(registry['approved_version'] == (approved[-1] if approved else None),
            'approved profile pointer differs from recorded decisions')
    if baseline_revision:
        baseline = prior_registry(root, baseline_revision)
        if baseline:
            current = {r['version']: r for r in releases}
            for old in baseline['releases']:
                new = current.get(old['version'])
                require(new is not None, 'published profile versions are immutable')
                immutable = set(old) - {'status', 'approval'}
                require(all(new.get(key) == old[key] for key in immutable),
                        'published profile snapshots and pins are immutable; add a version')
                if old['status'] == 'approved':
                    require(new == old, 'approved profile decisions are immutable')
    return {'registry_valid': True, 'profile_id': registry['profile_id'],
            'current_version': registry['current_version'], 'approved_version': registry['approved_version'],
            'versions': versions, 'baseline_revision': baseline_revision,
            'semantic_conformance_evaluated': False, 'approval_authenticity_verified': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline-revision', help='Exact base commit; rejects mutation of published snapshots')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.root, args.baseline_revision)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'representation profile invalid: {exc}\n')
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
