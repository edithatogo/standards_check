import unittest
from collections import Counter

from scripts.graph_ablation import EDGE_TYPES, ablate, shuffle_edges
from scripts.graph_development import compare, edges, load_fixture


class GraphAblationTests(unittest.TestCase):
    def test_full_factorial_retains_baseline_and_original_full_graph(self):
        data = load_fixture()
        report = ablate(data)
        prior = compare(data)
        self.assertEqual(report['eligible_pairs'], 250)
        self.assertFalse(report['equivalence_inferred'])
        for method, result in report['methods'].items():
            arms = result['arms']
            self.assertEqual(len(arms), 8)
            self.assertEqual(arms['none']['evaluation'], prior['methods'][method]['baseline'])
            self.assertEqual(arms['parent+crossref+dependency']['evaluation'], prior['methods'][method]['challenger'])
            self.assertEqual(len(result['negative_controls']), 20)
            for entry in arms.values():
                self.assertEqual(len(entry['paired']), 10)
                self.assertTrue(all(len(row['scores']) == 25 for row in entry['paired']))
            self.assertEqual(len(result['interactions']), 7)

    def test_shuffle_preserves_source_degree_type_and_destination_multiset(self):
        graph = edges(load_fixture())
        new = shuffle_edges(graph, 1)
        self.assertNotEqual(graph, new)
        for field in ('from', 'to'):
            self.assertEqual(Counter((e['type'], e[field]) for e in graph),
                             Counter((e['type'], e[field]) for e in new))
        self.assertTrue(all(e['from'] != e['to'] for e in new))
        self.assertTrue(all(e['control_only'] for e in new))
        self.assertEqual(new, shuffle_edges(graph, 1))
        self.assertEqual(set(e['type'] for e in new), set(EDGE_TYPES))

    def test_immovable_control_is_rejected(self):
        with self.assertRaises(ValueError):
            shuffle_edges([{'from':'A','to':'B','type':'dependency','anchor':'x'}], 0)

    def test_duplicate_query_and_cli_receipt(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from scripts import graph_ablation
        data = load_fixture()
        data['queries'].append(data['queries'][0])
        with self.assertRaises(ValueError):
            ablate(data)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'result.json'
            with patch('sys.argv', ['graph_ablation', '--output', str(output)]):
                graph_ablation.main()
            self.assertEqual(json.loads(output.read_text())['eligible_pairs'], 250)

    def test_empty_graph_control(self):
        self.assertEqual(shuffle_edges([], 0), [])
