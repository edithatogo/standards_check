import unittest

from scripts.orthogonal_experiments import compare, generated_pair, synthetic_comparison


class ExperimentTests(unittest.TestCase):
    def test_generated_pairs_conserve_partitions(self):
        for previous in (None, 3):
            case, legacy = generated_pair((1, 2, 3, 4), previous)
            counts = case['expected_counts']
            self.assertEqual(counts['identified'], 10)
            self.assertEqual(counts['screened'], 9)
            self.assertEqual(counts['assessed'], 7)
            self.assertEqual(counts['new_studies'], 4)
            self.assertEqual(counts['total_studies'], 4 + (previous or 0))
            self.assertEqual(legacy[('new_' if previous is not None else '') + 'records_identified'], 10)
            self.assertEqual(case['rust_input']['new_included'], {'studies': 4, 'reports': 4})
        for parts in ((-1, 2, 3, 4), (1, True, 3, 4), (1, 2, 3)):
            with self.assertRaises(ValueError):
                generated_pair(parts, None)
        with self.assertRaises(ValueError):
            generated_pair((1, 2, 3, 4), -1)

    def test_independent_groups_and_labels(self):
        row = {'id': 'a', 'family': 'f1', 'reference': 'equivalent', 'scores': {'equivalent': 0.1, 'narrower': 0.2, 'broader': 0.3, 'contradictory': 0.4, 'indeterminate': 0.5}}
        with self.assertRaises(ValueError):
            compare([row], [{**row, 'id': 'b'}], alpha=100)
        with self.assertRaises(ValueError):
            compare([row], [{**row, 'family': 'f2'}], alpha=100)
        with self.assertRaises(ValueError):
            compare([row], [{**row, 'id': 'b', 'family': 'f2', 'scores': {'equivalent': 0.1}}], alpha=100)
        result = compare([row], [{**row, 'id': 'b', 'family': 'f2'}], alpha=100)
        self.assertEqual(result['baseline']['accepted'], 1)
        self.assertEqual(result['split']['accepted'], 0)
        self.assertEqual(result['mondrian']['accepted'], 0)
        self.assertEqual(result['split']['set_misses'], 0)

    def test_synthetic_comparison(self):
        result = synthetic_comparison()
        self.assertEqual(result['scope'], 'synthetic_only')
        self.assertEqual(result['calibration_cases'], 495)
        self.assertEqual(result['test_cases'], 50)
        self.assertEqual(result['rank_disagreements'], 0)
        self.assertEqual(result['baseline']['accepted'], 50)
        self.assertEqual(result['baseline']['errors'], 20)
        self.assertEqual(result['baseline']['false_equivalences'], 16)
        for method in ('split', 'mondrian'):
            self.assertEqual(result[method]['accepted'], 35)
            self.assertEqual(result[method]['abstained'], 15)
            self.assertEqual(result[method]['errors'], 20)
            self.assertEqual(result[method]['false_equivalences'], 16)
