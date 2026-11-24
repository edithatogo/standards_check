import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.publication_contract import PROFILE, blob_sha, validate_versions, validate_evidence, replay_directory


class PublicationContractTests(unittest.TestCase):
    def test_immutable_version_and_approval_boundary(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / PROFILE
            directory.mkdir(parents=True)
            path = directory / '0.1.0.md'
            path.write_text('Draft\n')
            entry = {'version': '0.1.0', 'git_blob_sha': blob_sha(path.read_bytes()), 'status': 'draft', 'approval': None}
            registry = {'schema_version': 1, 'current_draft': '0.1.0', 'approved_version': None, 'versions': [entry]}
            self.assertEqual(validate_versions(root, registry)['0.1.0']['status'], 'draft')
            bad = copy.deepcopy(registry)
            bad['versions'][0]['status'] = 'approved'
            with self.assertRaisesRegex(ValueError, 'owner decision'):
                validate_versions(root, bad)
            path.write_text('Altered\n')
            with self.assertRaisesRegex(ValueError, 'snapshot changed'):
                validate_versions(root, registry)
            bad = copy.deepcopy(registry)
            bad['versions'][0]['git_blob_sha'] = blob_sha(path.read_bytes())
            with self.assertRaisesRegex(ValueError, 'history must be immutable'):
                validate_versions(root, bad, registry)

    def test_directory_conservation_and_held_qualification(self):
        fixture = {'schema_version': 1, 'status': 'historical_descriptive',
                   'directory': {'published_count': 2, 'lookup_counts': {'held': 2},
                                 'next_action_counts': {'retry': 2}, 'canonical_packs_promoted': 0},
                   'receipts': [{'sha256': 'a' * 64, 'url': 'https://github.com/example/repo'}],
                   'five_class_controls': {'n': 2, 'consensus': 1, 'correct_consensus': 1,
                                           'minilm_correct': 1, 'deberta_correct': 2, 'fixed': 1,
                                           'introduced': 0, 'natural_consensus': 0, 'qualified': False}}
        self.assertFalse(validate_evidence(fixture)['submission_authorized'])
        for mutate in (lambda d: d['directory']['lookup_counts'].update(held=3),
                       lambda d: d['directory'].update(canonical_packs_promoted=1),
                       lambda d: d['receipts'][0].update(sha256='wrong'),
                       lambda d: d['five_class_controls'].update(fixed=0),
                       lambda d: d['five_class_controls'].update(qualified=True)):
            bad = copy.deepcopy(fixture)
            mutate(bad)
            with self.assertRaises(ValueError):
                validate_evidence(bad)

    def test_replay_rejects_unpinned_archive(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'receipt.zip'
            path.write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError, 'artifact digest mismatch'):
                replay_directory({'receipts': [{'kind': 'directory', 'sha256': 'a' * 64}]}, path)
