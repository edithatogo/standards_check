"""Published profile snapshots cannot drift or acquire approval implicitly."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scripts.validate_representation_spec import REGISTRY, validate


ROOT = Path(__file__).resolve().parents[1]


class RepresentationSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = json.loads((ROOT / REGISTRY).read_text())
        paths = {REGISTRY}
        for release in self.registry['releases']:
            paths.add(release['document'])
            paths.update(item['path'] for item in release['implementation_contracts'])
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)

    def save(self):
        (self.root / REGISTRY).write_text(json.dumps(self.registry))

    def test_real_profile_is_a_draft_not_scientific_or_external_acceptance(self):
        result = validate(self.root)
        self.assertTrue(result['registry_valid'])
        self.assertEqual(result['current_version'], '0.1.0')
        self.assertIsNone(result['approved_version'])
        self.assertFalse(result['semantic_conformance_evaluated'])
        self.assertFalse(result['approval_authenticity_verified'])

    def test_document_and_current_contract_bytes_are_bound(self):
        release = self.registry['releases'][0]
        for relative in (release['document'], release['implementation_contracts'][0]['path']):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'digest'):
                    validate(self.root)
                path.write_bytes(original)

    def test_invalid_version_duplicate_missing_and_escaping_paths_rejected(self):
        original = copy.deepcopy(self.registry)
        mutations = [
            lambda r: r.update(current_version='latest'),
            lambda r: r['releases'].append(copy.deepcopy(r['releases'][0])),
            lambda r: r['releases'][0].update(document='../outside.md'),
            lambda r: r['releases'][0].update(sha256='unknown'),
            lambda r: r['releases'][0].update(previous_version='0.0.1'),
            lambda r: r['releases'][0]['requirement_ids'].pop(),
        ]
        for mutation in mutations:
            self.registry = copy.deepcopy(original)
            mutation(self.registry)
            self.save()
            with self.assertRaises(ValueError):
                validate(self.root)

    def test_approval_requires_a_hash_bound_decision_and_never_implies_endorsement(self):
        release = self.registry['releases'][0]
        release['status'] = 'approved'
        self.registry['approved_version'] = release['version']
        self.save()
        with self.assertRaisesRegex(ValueError, 'approval'):
            validate(self.root)
        release['approval'] = {
            'actor': 'synthetic-maintainer', 'decision': 'approve',
            'decision_url': 'https://github.com/example/project/pull/1',
            'date': '2026-11-24', 'specification_sha256': release['sha256'],
        }
        self.save()
        result = validate(self.root)
        self.assertEqual(result['approved_version'], '0.1.0')
        self.assertFalse(result['approval_authenticity_verified'])
        release['approval']['specification_sha256'] = '0' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'approval'):
            validate(self.root)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def test_published_snapshot_cannot_be_rehashed_in_place_but_new_version_can_be_added(self):
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'Freeze initial draft')
        baseline = self.git('rev-parse', 'HEAD')
        first = self.registry['releases'][0]
        old_bytes = (self.root / first['document']).read_bytes()
        changed = old_bytes + b'\nClarification.\n'
        (self.root / first['document']).write_bytes(changed)
        first['sha256'] = hashlib.sha256(changed).hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, 'immutable'):
            validate(self.root, baseline)
        (self.root / first['document']).write_bytes(old_bytes)
        first['sha256'] = hashlib.sha256(old_bytes).hexdigest()
        second = copy.deepcopy(first)
        second.update(version='0.1.1', previous_version='0.1.0', compatibility='clarification',
                      document=first['document'].replace('0.1.0', '0.1.1'),
                      sha256=hashlib.sha256(changed).hexdigest())
        (self.root / second['document']).write_bytes(changed)
        self.registry['releases'].append(second)
        self.registry['current_version'] = '0.1.1'
        self.save()
        self.assertEqual(validate(self.root, baseline)['current_version'], '0.1.1')

    def test_bad_or_unknown_baseline_is_not_ignored(self):
        with self.assertRaises(ValueError):
            validate(self.root, '--help')
        with self.assertRaises(ValueError):
            validate(self.root, '0' * 40)

    def test_historical_pin_syntax_and_additive_version_are_enforced(self):
        first = self.registry['releases'][0]
        second = copy.deepcopy(first)
        second.update(version='0.1.1', previous_version='0.1.0', compatibility='additive')
        self.registry['releases'].append(second)
        self.registry['current_version'] = '0.1.1'
        self.save()
        with self.assertRaisesRegex(ValueError, 'minor version'):
            validate(self.root)
        second['version'] = self.registry['current_version'] = '0.2.0'
        self.save()
        self.assertTrue(validate(self.root)['registry_valid'])
        first['implementation_contracts'][0] = {'path': '../outside.schema.json', 'sha256': '0' * 64}
        self.save()
        with self.assertRaisesRegex(ValueError, 'escapes'):
            validate(self.root)
        first['implementation_contracts'][0] = {'path': 'schemas/historical.json', 'sha256': 'invalid'}
        self.save()
        with self.assertRaisesRegex(ValueError, 'digest'):
            validate(self.root)


if __name__ == '__main__':
    unittest.main()
